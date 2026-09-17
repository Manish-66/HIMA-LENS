"use strict";
let map, markerLayer, allFeatures = [], filteredFeatures = [], selectedMarker, boundaryData, districtLayer, maskLayer, viewer, terrainProvider, billboardCollection, terrainRenderVersion = 0, last2DView, cesiumDistrictDataSource, cesiumBoundaryVersion = 0;
let roadLayer = null, polygonLayer = null, environmentalLayer = null, environmentalMeta = null;
let cesiumRoadsDataSource = null, cesiumPolygonsDataSource = null, cesiumEnvLayer = null;
let cachedRoadsGeoJSON = null;
let currentEnvChoice = "none", currentEnvOpacity = 0.8;
const MAP_CONFIG = { center:[31.75,77.1], zoom:8, minZoom:6, maxZoom:18 };
const layers = {};
document.addEventListener("DOMContentLoaded", init);

let loadingTimeoutId = null;

function showLoading(title, subtitle = "", badge = "LAYER SYNCHRONIZATION") {
  if (loadingTimeoutId) {
    clearTimeout(loadingTimeoutId);
    loadingTimeoutId = null;
  }
  const overlay = document.getElementById("map-loading");
  if (!overlay) return;
  const statusEl = document.getElementById("map-status");
  const subEl = document.getElementById("map-status-sub");
  const badgeEl = document.getElementById("map-loader-badge");
  if (statusEl && title) statusEl.textContent = title;
  if (subEl && subtitle !== undefined) subEl.textContent = subtitle;
  if (badgeEl && badge) badgeEl.textContent = badge;
  overlay.classList.remove("loaded");
}

function hideLoading(delay = 200) {
  const overlay = document.getElementById("map-loading");
  if (!overlay) return;
  if (loadingTimeoutId) clearTimeout(loadingTimeoutId);
  if (delay > 0) {
    loadingTimeoutId = setTimeout(() => {
      overlay.classList.add("loaded");
      loadingTimeoutId = null;
    }, delay);
  } else {
    overlay.classList.add("loaded");
    loadingTimeoutId = null;
  }
}

async function init() {
  initMap(); initControls();
  initExportModule();
  showLoading("INITIALIZING GEOSPATIAL ENGINE", "Loading landslide inventory & district boundaries…", "SYSTEM INITIALIZATION");
  try {
    const [inventory, boundaries] = await Promise.all([fetchJSON("/api/landslides"), fetchJSON("/api/district-boundaries")]);
    allFeatures = inventory.features.filter(validFeature); filteredFeatures = [...allFeatures]; boundaryData = boundaries;
    populateFilters(); renderDistrictBoundaries(); renderFeatures(true, false);
    loadCommunityReports();
    hideLoading(200);

    // Check if user jumped here from an Event Feed link
    const jumpData = sessionStorage.getItem("hima_jump_coords");
    if (jumpData) {
      try {
        const coords = JSON.parse(jumpData);
        sessionStorage.removeItem("hima_jump_coords");
        setTimeout(() => {
          if (map) {
            map.flyTo([coords.lat, coords.lng], coords.zoom || 13, { duration: 1.5 });
          }
        }, 500);
      } catch (e) {
        console.warn("Failed to parse jump coordinates", e);
      }
    }
  } catch (error) {
    console.error(error);
    showLoading("DATASTREAM OFFLINE", "Could not connect to geospatial API — please refresh", "ERROR");
  }
}

async function fetchJSON(url) { const response = await fetch(url, {headers:{Accept:"application/json"}}); if (!response.ok) throw Error(`HTTP ${response.status}`); return response.json(); }

function initMap() {
  map = L.map("map", {center:MAP_CONFIG.center, zoom:MAP_CONFIG.zoom, minZoom:MAP_CONFIG.minZoom, maxZoom:MAP_CONFIG.maxZoom, zoomControl:false, preferCanvas:true});
  L.control.zoom({position:"bottomright"}).addTo(map);
  layers.standard = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {maxZoom:19, attribution:"© OpenStreetMap contributors"});
  layers.satellite = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {maxZoom:18, attribution:"Tiles © Esri"});
  layers.terrain = L.tileLayer("https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png", {maxZoom:17, attribution:"© OpenTopoMap © OpenStreetMap contributors"});
  layers.standard.addTo(map);
  markerLayer = L.markerClusterGroup({
    chunkedLoading: true,
    chunkInterval: 150,
    chunkDelay: 10,
    removeOutsideVisibleBounds: true,
    spiderfyOnMaxZoom: true,
    spiderfyDistanceMultiplier: 1.4,
    showCoverageOnHover: false,
    zoomToBoundsOnClick: true,
    animate: true,
    animateAddingMarkers: false,
    maxClusterRadius: 50,
    disableClusteringAtZoom: 16
  }).addTo(map);
  map.on("mousemove", event => document.getElementById("cursor-coords").innerHTML = `${event.latlng.lat.toFixed(4)}° N, ${event.latlng.lng.toFixed(4)}° E &bull; EPSG:4326 &bull; HP-GRID`);
}

function validFeature(f) { return f?.geometry?.type === "Point" && Array.isArray(f.geometry.coordinates) && f.geometry.coordinates.length >= 2; }
function property(props, names, fallback="Not available") { for (const name of names) { const value=props?.[name]; if(value !== undefined && value !== null && String(value).trim()) return String(value).trim(); } return fallback; }
function p(f, field, fallback="Not recorded in source") { const keys={district:["district","District","DISTRICT"],activity:["activity","Activity","ACTIVITY","activity_status","activityStatus","status"],movement:["movement_type","movementType","movement","MOVEMENT_T","MOVEMENT_","MOVEMENT","movement_t"],material:["material_type","materialType","material","MATERIAL_T","MATERIAL","material_t"],year:["year","Year","period","Period","recorded_year","recordedYear"]}; return property(f.properties,keys[field],fallback); }

function renderFeatures(fit=false, focus3d=false) {
  markerLayer.clearLayers(); selectedMarker=null; const markers=[], positions=[];
  const showPoints = document.getElementById("toggle-points") ? document.getElementById("toggle-points").checked : true;
  filteredFeatures.forEach(feature => {
    const [lng,lat]=feature.geometry.coordinates.map(Number);
    if (!Number.isFinite(lat)||!Number.isFinite(lng)) return;
    if (showPoints) {
      const marker=L.marker([lat,lng],{icon:leafletIcon(feature),keyboard:false,riseOnHover:true});
      marker.on("click",()=>{ highlight(marker,feature); drawer(feature,lat,lng); });
      markers.push(marker);
    }
    positions.push([lat,lng]);
  });
  if (showPoints) markerLayer.addLayers(markers);
  document.getElementById("visible-count").textContent=filteredFeatures.length.toLocaleString("en-IN");
  if(fit&&positions.length) map.fitBounds(L.latLngBounds(positions),{padding:[60,60],maxZoom:13});
  if (viewer) renderCesiumPoints(focus3d);
}

function markerVisual(feature) { const activity=p(feature,"activity","").toLowerCase(), movement=p(feature,"movement","").toLowerCase(); if(activity.includes("active")) return {kind:"active",color:"#38bdf8"}; if(movement.includes("fall")) return {kind:"fall",color:"#f59e0b"}; if(movement.includes("flow")) return {kind:"flow",color:"#a855f7"}; if(movement.includes("slide")) return {kind:"slide",color:"#10b981"}; if(movement.includes("debris")) return {kind:"debris",color:"#ef4444"}; return {kind:"record",color:"#10b981"}; }
const iconCache={};
function landslideIcon(kind,color) { const cacheKey=`${kind}-${color}`; if(iconCache[cacheKey]) return iconCache[cacheKey]; const glyph={active:"●",fall:"◆",flow:"≈",slide:"▲",debris:"⬟",record:"●"}[kind]||"●"; const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 22 22"><circle cx="11" cy="11" r="9.5" fill="#071f19" fill-opacity=".82" stroke="white" stroke-width="1.4"/><text x="11" y="15" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="bold" fill="${color}">${glyph}</text></svg>`; iconCache[cacheKey]=`data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`; return iconCache[cacheKey]; }
function leafletIcon(feature) { const visual=markerVisual(feature); return L.divIcon({className:"landslide-leaflet-icon",html:`<img alt="" src="${landslideIcon(visual.kind,visual.color)}">`,iconSize:[22,22],iconAnchor:[11,11]}); }
function highlight(marker, feature) { if(selectedMarker) selectedMarker.getElement()?.classList.remove("selected-landslide-icon"); marker.feature=feature; marker.getElement()?.classList.add("selected-landslide-icon"); selectedMarker=marker; }

function drawer(feature,lat,lng) {
  const props=feature.properties||{}, set=(id,value)=>document.getElementById(id).textContent=value;
  set("drawer-title",property(props,["id_land","id"],"Mapped Feature"));
  set("drawer-district",p(feature,"district"));
  set("drawer-year",p(feature,"year"));
  set("drawer-activity",p(feature,"activity"));
  set("drawer-movement",p(feature,"movement"));
  set("drawer-material",p(feature,"material"));
  set("drawer-style",property(props,["style","STYLE"]));
  const road=Number(props.distance_to_road_m);
  set("drawer-road-distance",Number.isFinite(road)?`${road.toFixed(1)} m`:"Not recorded in source");
  set("drawer-trigger",property(props,["triggering","trigger" ],"Not recorded in source"));
  set("drawer-geology",property(props,["geology"],"Not recorded in source"));
  set("drawer-hydrology",property(props,["hydrologic","hydrology"],"Not recorded in source"));
  set("drawer-landuse",property(props,["landuse_la","landuse"],"Not recorded in source"));
  set("drawer-coords",`${lat.toFixed(5)}° N, ${lng.toFixed(5)}° E`);
  document.getElementById("feature-drawer").classList.add("open");
}

function polygonDrawer(feature, lat, lng) {
  const props = feature.properties || {}, set = (id, val) => document.getElementById(id).textContent = val;
  set("drawer-title", props.id || "Landslide Hazard Zone");
  set("drawer-district", props.district || "Mandi");
  set("drawer-year", props.toposheet ? `Toposheet: ${props.toposheet}` : "Mapped Survey");
  set("drawer-activity", "Hazard Polygon");
  set("drawer-movement", "Mapped Zone");
  set("drawer-material", props.material_type || "Debris / Soil");
  set("drawer-style", props.area_sq_m ? `${Number(props.area_sq_m).toLocaleString()} m²` : "Not recorded");
  set("drawer-road-distance", "Zonation Feature");
  set("drawer-trigger", props.geomorphology || "Slope Hazard");
  set("drawer-geology", props.geomorphology || "Dissected Hill Terrain");
  set("drawer-hydrology", "Catchment Basin");
  set("drawer-landuse", props.lulc || "Not recorded");
  set("drawer-coords", `${lat.toFixed(5)}° N, ${lng.toFixed(5)}° E`);
  document.getElementById("feature-drawer").classList.add("open");
}

function roadDrawer(feature, lat, lng) {
  const props = feature.properties || {}, set = (id, val) => document.getElementById(id).textContent = val;
  set("drawer-title", props.name || "Road Segment");
  set("drawer-district", "Mandi");
  set("drawer-year", "Road Infrastructure");
  set("drawer-activity", "Transportation Network");
  set("drawer-movement", props.category || "Rural Road");
  set("drawer-material", props.length_km ? `${props.length_km} km` : "Not recorded");
  set("drawer-style", `ID: ${props.id || 'N/A'}`);
  set("drawer-road-distance", "0.0 m (Road Centerline)");
  set("drawer-trigger", "All-Weather Connectivity");
  set("drawer-geology", "Mandi Transportation Grid");
  set("drawer-hydrology", "Culvert / Drainage Alignment");
  set("drawer-landuse", "Public Works Department");
  set("drawer-coords", `${lat.toFixed(5)}° N, ${lng.toFixed(5)}° E`);
  document.getElementById("feature-drawer").classList.add("open");
}

function districtName(feature) { return property(feature?.properties,["district","name","lgd_districtname"],""); }
function populateFilters() { const districts=[...new Set((boundaryData?.features||[]).map(districtName).filter(Boolean))].sort((a,b)=>a.localeCompare(b)); populate("district",districts); populate("year",unique("year").sort().reverse()); populate("activity",unique("activity")); populate("movement",unique("movement")); document.getElementById("district-count").textContent=districts.length.toLocaleString("en-IN"); }
function unique(field) { return [...new Set(allFeatures.map(f=>p(f,field,"")).filter(Boolean))].sort((a,b)=>a.localeCompare(b,undefined,{numeric:true})); }
function populate(id, values) { const el=document.getElementById(id); values.forEach(value=>el.add(new Option(value,value))); }

function pointInPolygon(point, vs) {
  const x = point[0], y = point[1];
  let inside = false;
  for (let i = 0, j = vs.length - 1; i < vs.length; j = i++) {
    const xi = vs[i][0], yi = vs[i][1];
    const xj = vs[j][0], yj = vs[j][1];
    const intersect = ((yi > y) !== (yj > y)) && (x < (xj - x) * (y - yi) / (yj - yi) + xi);
    if (intersect) inside = !inside;
  }
  return inside;
}

function isPointInDistrict(lat, lng, distFeature, distBounds) {
  if (!distFeature) return true;
  if (distBounds && !distBounds.contains([lat, lng])) return false;
  const geom = distFeature.geometry;
  if (!geom) return true;
  const pt = [lng, lat];
  if (geom.type === "Polygon") {
    return pointInPolygon(pt, geom.coordinates[0]);
  } else if (geom.type === "MultiPolygon") {
    return geom.coordinates.some(poly => pointInPolygon(pt, poly[0]));
  }
  return true;
}

function applyFilters() {
  const query = id => document.getElementById(id).value;
  const district = query("district"), year = query("year"), activity = query("activity"), movement = query("movement");

  let distFeature = null, distBounds = null;
  if (district !== "all" && boundaryData?.features) {
    distFeature = boundaryData.features.find(f => districtName(f).toLowerCase() === district.toLowerCase());
    if (distFeature) distBounds = L.geoJSON(distFeature).getBounds();
  }

  filteredFeatures = allFeatures.filter(f => {
    const [lng, lat] = f.geometry.coordinates.map(Number);
    if (!Number.isFinite(lat) || !Number.isFinite(lng)) return false;

    if (district !== "all") {
      const stated = p(f, "district").toLowerCase();
      if (stated !== district.toLowerCase()) return false;
      if (distFeature && !isPointInDistrict(lat, lng, distFeature, distBounds)) return false;
    }
    if (year !== "all" && p(f, "year") !== year) return false;
    if (activity !== "all" && p(f, "activity").toLowerCase() !== activity.toLowerCase()) return false;
    if (movement !== "all" && p(f, "movement").toLowerCase() !== movement.toLowerCase()) return false;
    return true;
  });

  isolateDistrict(district);
  renderFeatures(district === "all", true);
  renderCommunityReports(district);
  const polyToggle = document.getElementById("toggle-polygons");
  if (polyToggle && polyToggle.checked) togglePolygons(true);
}

function districtStyle(feature, selected="all") { const active=districtName(feature).toLowerCase()===String(selected).toLowerCase(); return {color:active?"#74f0b7":"#376857",weight:active?3:1,opacity:active?1:.72,fillColor:active?"#1bb77b":"#2b6752",fillOpacity:active?.15:.018,interactive:true}; }
function renderDistrictBoundaries() {
  districtLayer=L.geoJSON(boundaryData,{style:feature=>districtStyle(feature),onEachFeature:(feature,layer)=>{const name=districtName(feature);layer.bindTooltip(name,{sticky:true,direction:"top",className:"district-map-tooltip"});layer.on("click",event=>{L.DomEvent.stopPropagation(event);document.getElementById("district").value=name;applyFilters();});layer.on("mouseover",()=>{if(document.getElementById("district").value==="all")layer.setStyle({...districtStyle(feature),weight:2,fillOpacity:.07,color:"#72efb9"});});layer.on("mouseout",()=>styleDistrictBoundaries(document.getElementById("district").value));}}).addTo(map);
}
function styleDistrictBoundaries(selected) { districtLayer?.eachLayer(layer=>layer.setStyle(districtStyle(layer.feature,selected))); }

function isolateDistrict(district) {
  if(maskLayer)map.removeLayer(maskLayer); const banner=document.getElementById("active-district-banner"); styleDistrictBoundaries(district);
  if(district==="all") { banner.hidden=true; updateCesiumDistrictBoundary(null); return; }
  const selectedLayer=Object.values(districtLayer?._layers||{}).find(layer=>districtName(layer.feature).toLowerCase()===district.toLowerCase()), feature=selectedLayer?.feature; if(!feature)return;
  const ring=feature.geometry.coordinates[0], world=[[-180,-85],[180,-85],[180,85],[-180,85],[-180,-85]]; maskLayer=L.geoJSON({type:"Feature",geometry:{type:"Polygon",coordinates:[world,ring]}},{style:{stroke:false,fillColor:"#07120f",fillOpacity:.48,fillRule:"evenodd",interactive:false}}).addTo(map); selectedLayer.bringToFront(); if(markerLayer.bringToFront)markerLayer.bringToFront(); map.fitBounds(selectedLayer.getBounds(),{padding:[70,70],maxZoom:10}); banner.hidden=false; banner.textContent=`ACTIVE DISTRICT · ${district.toUpperCase()} · ${filteredFeatures.length.toLocaleString("en-IN")} RECORDS`; updateCesiumDistrictBoundary(feature);
}

async function updateCesiumDistrictBoundary(feature) { if(!viewer)return; const version=++cesiumBoundaryVersion; if(cesiumDistrictDataSource){viewer.dataSources.remove(cesiumDistrictDataSource,true);cesiumDistrictDataSource=null;} if(!feature){viewer.scene.requestRender();return;} try{const source=await Cesium.GeoJsonDataSource.load(feature,{stroke:Cesium.Color.fromCssColorString("#74f0b7"),strokeWidth:3,fill:Cesium.Color.fromCssColorString("#1bb77b").withAlpha(.14),clampToGround:true});if(version!==cesiumBoundaryVersion)return;cesiumDistrictDataSource=await viewer.dataSources.add(source);viewer.scene.requestRender();}catch(error){console.warn("District outline could not be added to 3D terrain.",error);} }
function switchBase(name) {
  showLoading("SWITCHING BASEMAP", `Rendering ${name.toUpperCase()} layer tiles…`, "BASEMAP SELECTOR");
  Object.values(layers).forEach(layer=>map.removeLayer(layer));
  if (layers[name]) layers[name].addTo(map);
  hideLoading(300);
}

// --- ARCGIS OVERLAY MANAGEMENT ---
async function toggleRoads(visible) {
  updateCesiumRoads(visible);
  if (!visible) {
    if (roadLayer && map.hasLayer(roadLayer)) map.removeLayer(roadLayer);
    return;
  }
  showLoading("STREAMING ROAD NETWORK", "Fetching Mandi PWD road infrastructure…", "INFRASTRUCTURE LAYER");
  if (!cachedRoadsGeoJSON) {
    try {
      cachedRoadsGeoJSON = await fetchJSON("/api/roads");
    } catch (e) {
      console.error("Failed to load roads", e);
      hideLoading(0);
      return;
    }
  }
  if (!roadLayer) {
    roadLayer = L.geoJSON(cachedRoadsGeoJSON, {
      style: () => ({
        color: "#fb923c",
        weight: 2.2,
        opacity: 0.88,
        lineCap: "round",
        lineJoin: "round"
      }),
      onEachFeature: (feature, layer) => {
        const props = feature.properties || {};
        const name = props.name || "Road Segment";
        const cat = props.category || "Rural Road";
        const len = props.length_km ? `${props.length_km} km` : "";
        layer.bindTooltip(`<strong>${name}</strong><br><span style="color:#a7f3d0;font-size:9px;">${cat} ${len ? '• ' + len : ''}</span>`, {
          sticky: true,
          direction: "top",
          className: "road-map-tooltip"
        });
        layer.on("mouseover", () => layer.setStyle({ color: "#fef08a", weight: 4.5, opacity: 1 }));
        layer.on("mouseout", () => layer.setStyle({ color: "#fb923c", weight: 2.2, opacity: 0.88 }));
        layer.on("click", (e) => {
          L.DomEvent.stopPropagation(e);
          roadDrawer(feature, e.latlng.lat, e.latlng.lng);
        });
      }
    });
  }
  roadLayer.addTo(map);
  roadLayer.bringToBack();
  if (districtLayer && districtLayer.bringToBack) districtLayer.bringToBack();
  hideLoading(250);
}

async function togglePolygons(visible) {
  updateCesiumPolygons(visible);
  if (!visible) {
    if (polygonLayer && map.hasLayer(polygonLayer)) map.removeLayer(polygonLayer);
    return;
  }
  const district = document.getElementById("district").value;
  const targetUrl = district && district.toLowerCase() === "mandi"
    ? "/api/landslide-polygons?district=mandi"
    : (district && district !== "all" ? `/api/landslide-polygons?district=${encodeURIComponent(district)}` : "/api/landslide-polygons");

  showLoading("LOADING HAZARD ZONES", "Streaming polygon geometries & hazard envelopes…", "HAZARD BOUNDARIES");
  try {
    const polyData = await fetchJSON(targetUrl);
    if (polygonLayer && map.hasLayer(polygonLayer)) map.removeLayer(polygonLayer);
    polygonLayer = L.geoJSON(polyData, {
      style: (feature) => {
        const mat = (feature.properties?.material_type || "").toLowerCase();
        let col = "#f59e0b";
        if (mat.includes("rock")) col = "#ef4444";
        else if (mat.includes("debris") || mat.includes("soil")) col = "#f97316";
        return {
          color: col,
          weight: 1.2,
          opacity: 0.9,
          fillColor: col,
          fillOpacity: 0.32
        };
      },
      onEachFeature: (feature, layer) => {
        const props = feature.properties || {};
        const areaStr = props.area_sq_m ? `${Number(props.area_sq_m).toLocaleString()} m²` : "";
        layer.bindTooltip(`<strong>${props.id || 'Hazard Zone'}</strong><br><span style="color:#fde68a;font-size:9px;">${props.district || ''} ${areaStr ? '• ' + areaStr : ''}</span>`, {
          sticky: true,
          direction: "top",
          className: "polygon-map-tooltip"
        });
        layer.on("mouseover", () => layer.setStyle({ weight: 2.5, fillOpacity: 0.65 }));
        layer.on("mouseout", () => layer.setStyle({ weight: 1.2, fillOpacity: 0.32 }));
        layer.on("click", (e) => {
          L.DomEvent.stopPropagation(e);
          polygonDrawer(feature, e.latlng.lat, e.latlng.lng);
        });
      }
    }).addTo(map);
    polygonLayer.bringToBack();
    if (districtLayer && districtLayer.bringToBack) districtLayer.bringToBack();
  } catch (err) {
    console.error("Failed to load polygons", err);
  } finally {
    hideLoading(250);
  }
}

async function toggleEnvironmental(choice, opacity) {
  currentEnvChoice = choice;
  updateCesiumEnvironmental(choice, opacity);
  const opacityWrap = document.getElementById("env-opacity-wrap");
  const envLegendCard = document.getElementById("env-legend-card");
  const envLegendTitle = document.getElementById("env-legend-title");
  const envLegendItems = document.getElementById("env-legend-items");

  if (environmentalLayer && map.hasLayer(environmentalLayer)) {
    map.removeLayer(environmentalLayer);
    environmentalLayer = null;
  }

  if (choice === "none") {
    opacityWrap.style.display = "none";
    envLegendCard.style.display = "none";
    return;
  }

  const layerTitles = {
    lulc: "LAND COVER (LULC 2023)",
    geomorphology: "GEOMORPHOLOGY",
    lithology: "LITHOLOGY (BEDROCK)"
  };
  const titleText = layerTitles[choice] || "ENVIRONMENTAL RASTER";
  showLoading(`SYNCING ${titleText}`, "Overlaying 10m high-resolution raster…", "THEMATIC RASTER");

  if (!environmentalMeta) {
    try {
      const res = await fetchJSON("/api/environmental-layers");
      environmentalMeta = res.layers || {};
    } catch (e) {
      console.error("Failed to load environmental metadata", e);
      hideLoading(0);
      return;
    }
  }

  const meta = environmentalMeta[choice];
  if (!meta) {
    hideLoading(0);
    return;
  }

  opacityWrap.style.display = "block";
  environmentalLayer = L.imageOverlay(meta.url, meta.bounds, {
    opacity: opacity,
    interactive: false
  }).addTo(map);
  environmentalLayer.bringToBack();
  if (districtLayer && districtLayer.bringToBack) districtLayer.bringToBack();

  envLegendTitle.textContent = meta.title.toUpperCase();
  envLegendItems.innerHTML = meta.legend.map(item =>
    `<div class="env-legend-chip" title="${item.label}">
      <span class="env-chip-swatch" style="background:${item.color};box-shadow:0 0 8px ${item.color}90;"></span>
      <span class="env-chip-label">${item.label}</span>
    </div>`
  ).join("");
  envLegendCard.style.display = "block";
  hideLoading(300);
}

// --- CESIUM 3D INTEGRATION & OVERLAY MIRRORING ---
async function updateCesiumRoads(visible) {
  if (!viewer) return;
  if (cesiumRoadsDataSource) {
    viewer.dataSources.remove(cesiumRoadsDataSource, true);
    cesiumRoadsDataSource = null;
  }
  if (!visible) {
    viewer.scene.requestRender();
    return;
  }
  if (!cachedRoadsGeoJSON) {
    try {
      cachedRoadsGeoJSON = await fetchJSON("/api/roads");
    } catch (e) {
      console.warn("Failed to fetch roads for 3D", e);
      return;
    }
  }
  try {
    cesiumRoadsDataSource = await Cesium.GeoJsonDataSource.load(cachedRoadsGeoJSON, {
      stroke: Cesium.Color.fromCssColorString("#fb923c"),
      strokeWidth: 3,
      clampToGround: true
    });
    const entities = cesiumRoadsDataSource.entities.values;
    for (let i = 0; i < entities.length; i++) {
      const entity = entities[i];
      entity._himaType = "road";
      if (entity.polyline) {
        entity.polyline.clampToGround = true;
      }
    }
    await viewer.dataSources.add(cesiumRoadsDataSource);
    viewer.scene.requestRender();
  } catch (err) {
    console.warn("Could not add roads to 3D terrain", err);
  }
}

async function updateCesiumPolygons(visible) {
  if (!viewer) return;
  if (cesiumPolygonsDataSource) {
    viewer.dataSources.remove(cesiumPolygonsDataSource, true);
    cesiumPolygonsDataSource = null;
  }
  if (!visible) {
    viewer.scene.requestRender();
    return;
  }
  const district = document.getElementById("district")?.value || "all";
  const targetUrl = district && district.toLowerCase() === "mandi"
    ? "/api/landslide-polygons?district=mandi"
    : (district && district !== "all" ? `/api/landslide-polygons?district=${encodeURIComponent(district)}` : "/api/landslide-polygons");

  set3dStatus("PROJECTING 3D HAZARD POLYGONS ONTO TERRAIN…", true);
  try {
    const polyData = await fetchJSON(targetUrl);
    cesiumPolygonsDataSource = await Cesium.GeoJsonDataSource.load(polyData, {
      fill: Cesium.Color.fromCssColorString("#f59e0b").withAlpha(0.48),
      stroke: Cesium.Color.fromCssColorString("#d97706"),
      strokeWidth: 2,
      clampToGround: true
    });
    const entities = cesiumPolygonsDataSource.entities.values;
    for (let i = 0; i < entities.length; i++) {
      const entity = entities[i];
      entity._himaType = "polygon";
      if (entity.polygon) {
        entity.polygon.classificationType = Cesium.ClassificationType.BOTH;
      }
    }
    await viewer.dataSources.add(cesiumPolygonsDataSource);
    viewer.scene.requestRender();
  } catch (err) {
    console.warn("Could not add polygons to 3D terrain", err);
  } finally {
    set3dStatus("", false);
  }
}

async function updateCesiumEnvironmental(choice, opacity) {
  if (!viewer) return;
  if (cesiumEnvLayer) {
    viewer.imageryLayers.remove(cesiumEnvLayer, true);
    cesiumEnvLayer = null;
  }
  if (choice === "none") {
    viewer.scene.requestRender();
    return;
  }
  if (!environmentalMeta) {
    try {
      const res = await fetchJSON("/api/environmental-layers");
      environmentalMeta = res.layers || {};
    } catch (e) {
      console.warn("Failed to load environmental metadata for 3D", e);
      return;
    }
  }
  const meta = environmentalMeta[choice];
  if (!meta) return;
  try {
    const rect = Cesium.Rectangle.fromDegrees(
      meta.bounds[0][1], meta.bounds[0][0], meta.bounds[1][1], meta.bounds[1][0]
    );
    let provider;
    if (typeof Cesium.SingleTileImageryProvider.fromUrl === "function") {
      provider = await Cesium.SingleTileImageryProvider.fromUrl(meta.url, { rectangle: rect });
    } else {
      provider = new Cesium.SingleTileImageryProvider({
        url: meta.url,
        rectangle: rect
      });
    }
    cesiumEnvLayer = viewer.imageryLayers.addImageryProvider(provider);
    cesiumEnvLayer.alpha = opacity;
    viewer.scene.requestRender();
  } catch (err) {
    console.warn("Could not add environmental overlay to 3D terrain", err);
  }
}

async function syncCesiumAllOverlays() {
  if (!viewer) return;
  const showPoints = document.getElementById("toggle-points") ? document.getElementById("toggle-points").checked : true;
  const showPolygons = document.getElementById("toggle-polygons") ? document.getElementById("toggle-polygons").checked : false;
  const showRoads = document.getElementById("toggle-roads") ? document.getElementById("toggle-roads").checked : false;
  const envChoice = document.querySelector('input[name="env-layer-choice"]:checked')?.value || "none";

  if (billboardCollection) billboardCollection.show = showPoints;
  await Promise.all([
    updateCesiumRoads(showRoads),
    updateCesiumPolygons(showPolygons),
    updateCesiumEnvironmental(envChoice, currentEnvOpacity)
  ]);
}

async function initCesium() {
  const mapCenter=map.getCenter(); last2DView={center:[mapCenter.lat,mapCenter.lng],zoom:map.getZoom()};
  showLoading("PREPARING 3D TERRAIN", "Initializing Cesium 3D elevation viewport…", "3D TERRAIN ENGINE");
  if(viewer) {
    document.getElementById("cesium-map").classList.add("active");
    document.getElementById("map").classList.add("hidden");
    viewer.resize();
    focusCesiumOnMap(true);
    await syncCesiumAllOverlays();
    hideLoading(300);
    return;
  }
  await new Promise(resolve => setTimeout(resolve, 60));
  const target=document.getElementById("cesium-map"); target.classList.add("active"); document.getElementById("map").classList.add("hidden");
  const token=window.HIMA_CONFIG?.cesiumIonToken;
  if(token) Cesium.Ion.defaultAccessToken=token;

  // High-resolution satellite imagery fallback (ESRI World Imagery, needs no API key)
  const esriSatellite=new Cesium.UrlTemplateImageryProvider({
    url:"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    credit:"Tiles © Esri"
  });

  viewer=new Cesium.Viewer("cesium-map",{
    baseLayer:new Cesium.ImageryLayer(esriSatellite),
    baseLayerPicker:false,
    geocoder:false,
    animation:false,
    timeline:false,
    homeButton:false,
    sceneModePicker:false,
    navigationHelpButton:false,
    requestRenderMode:false
  });
  viewer.resize();

  const selectedDistrict=document.getElementById("district").value;
  if(selectedDistrict!=="all") updateCesiumDistrictBoundary(boundaryData?.features?.find(feature=>districtName(feature).toLowerCase()===selectedDistrict.toLowerCase()));
  focusCesiumOnMap(false);

  if(token) {
    showLoading("STREAMING 3D SATELLITE & ELEVATION", "Downloading digital elevation model & aerial photography…", "3D TERRAIN ENGINE");
    try {
      const [satelliteRes, terrainRes] = await Promise.allSettled([
        Cesium.createWorldImageryAsync({style:Cesium.IonWorldImageryStyle.AERIAL}),
        Cesium.createWorldTerrainAsync({requestVertexNormals:true})
      ]);
      if(satelliteRes.status === "fulfilled" && satelliteRes.value) {
        viewer.imageryLayers.removeAll();
        const sat = satelliteRes.value;
        if(sat instanceof Cesium.ImageryLayer) viewer.imageryLayers.add(sat);
        else viewer.imageryLayers.addImageryProvider(sat);
      }
      if(terrainRes.status === "fulfilled" && terrainRes.value) {
        terrainProvider = terrainRes.value;
        if("terrain" in viewer) viewer.terrain = terrainRes.value;
        else viewer.terrainProvider = terrainRes.value;
        viewer.scene.globe.depthTestAgainstTerrain = true;
      }
    } catch(error) {
      console.warn("Cesium Ion imagery/terrain could not load; retaining ESRI satellite fallback.",error);
    }
  } else {
    console.log("Using ESRI satellite basemap for 3D view.");
    viewer.scene.globe.depthTestAgainstTerrain = false;
  }

  showLoading("PROJECTING 3D LANDSLIDE FEATURES", "Sampling surface terrain elevations for records…", "3D TERRAIN ENGINE");
  await renderCesiumPoints(false);
  await syncCesiumAllOverlays();
  hideLoading(350);

  // Multi-entity 3D picking handler for points, roads, and polygons
  viewer.screenSpaceEventHandler.setInputAction(movement => {
    const picked = viewer.scene.pick(movement.position);
    if (!picked) return;
    const entity = picked.id;
    if (!entity) return;

    // 1. Point landslide billboard
    if (entity.type === "Feature" || entity._himaType === "point") {
      const [lng, lat] = entity.geometry.coordinates;
      drawer(entity, Number(lat), Number(lng));
      return;
    }

    // 2. Road entity from GeoJsonDataSource
    if (entity._himaType === "road" || (entity.properties && entity.properties.hasProperty && entity.properties.hasProperty("category"))) {
      const props = {};
      if (entity.properties) {
        const propNames = entity.properties.propertyNames || [];
        propNames.forEach(name => {
          const val = entity.properties[name];
          props[name] = val && typeof val.getValue === "function" ? val.getValue() : val;
        });
      }
      const carto = viewer.scene.globe.ellipsoid.cartesianToCartographic(viewer.camera.pickEllipsoid(movement.position) || Cesium.Cartesian3.ZERO);
      const lat = carto ? Cesium.Math.toDegrees(carto.latitude) : 31.75;
      const lng = carto ? Cesium.Math.toDegrees(carto.longitude) : 77.10;
      roadDrawer({ properties: props }, lat, lng);
      return;
    }

    // 3. Polygon entity from GeoJsonDataSource
    if (entity._himaType === "polygon" || (entity.properties && entity.properties.hasProperty && (entity.properties.hasProperty("area_sq_m") || entity.properties.hasProperty("lulc")))) {
      const props = {};
      if (entity.properties) {
        const propNames = entity.properties.propertyNames || [];
        propNames.forEach(name => {
          const val = entity.properties[name];
          props[name] = val && typeof val.getValue === "function" ? val.getValue() : val;
        });
      }
      const carto = viewer.scene.globe.ellipsoid.cartesianToCartographic(viewer.camera.pickEllipsoid(movement.position) || Cesium.Cartesian3.ZERO);
      const lat = carto ? Cesium.Math.toDegrees(carto.latitude) : 31.75;
      const lng = carto ? Cesium.Math.toDegrees(carto.longitude) : 77.10;
      polygonDrawer({ properties: props }, lat, lng);
      return;
    }
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
}

// --- OPTIMIZED 3D TERRAIN RENDERING ENGINE ---
const terrainHeightCache = new Map();
const cartesianPositionCache = new Map();
let sharedNearFarScalar = null;

async function renderCesiumPoints(focus = false) {
  if (!viewer) return;
  const version = ++terrainRenderVersion;

  if (!sharedNearFarScalar) {
    sharedNearFarScalar = new Cesium.NearFarScalar(1000, 1.1, 150000, 0.52);
  }

  // Reuse existing BillboardCollection to preserve GPU vertex buffers & texture atlas
  if (!billboardCollection) {
    billboardCollection = viewer.scene.primitives.add(new Cesium.BillboardCollection({ scene: viewer.scene }));
  } else {
    billboardCollection.removeAll();
  }

  const showPoints = document.getElementById("toggle-points") ? document.getElementById("toggle-points").checked : true;
  billboardCollection.show = showPoints;

  const records = [];
  const uncachedIndices = [];
  const uncachedPositions = [];

  for (let i = 0; i < filteredFeatures.length; i++) {
    const feature = filteredFeatures[i];
    const coords = feature.geometry.coordinates;
    const lng = Number(coords[0]);
    const lat = Number(coords[1]);
    if (!Number.isFinite(lat) || !Number.isFinite(lng)) continue;

    // Fast coordinate key (5 decimals = ~1m precision)
    const key = (feature.id || `${lat.toFixed(5)}_${lng.toFixed(5)}`);
    const record = { feature, lng, lat, key, height: 0 };
    records.push(record);

    if (terrainHeightCache.has(key)) {
      record.height = terrainHeightCache.get(key);
    } else {
      uncachedIndices.push(records.length - 1);
      uncachedPositions.push(Cesium.Cartographic.fromDegrees(lng, lat));
    }
  }

  // Only sample terrain heights for points NOT yet in the cache
  if (terrainProvider && uncachedPositions.length > 0) {
    set3dStatus(`STREAMING 3D TERRAIN ELEVATION (${uncachedPositions.length.toLocaleString("en-IN")} uncached)…`, true);
    try {
      await Cesium.sampleTerrainMostDetailed(terrainProvider, uncachedPositions);
      for (let j = 0; j < uncachedPositions.length; j++) {
        const h = Number.isFinite(uncachedPositions[j].height) ? uncachedPositions[j].height : 0;
        const recIdx = uncachedIndices[j];
        records[recIdx].height = h;
        terrainHeightCache.set(records[recIdx].key, h);
      }
    } catch (error) {
      console.warn("Terrain height sampling failed; using cached/ellipsoid height fallback.", error);
    }
  }

  if (version !== terrainRenderVersion) return;

  // Batch-add billboards using cached Cartesian3 positions
  for (let i = 0; i < records.length; i++) {
    const rec = records[i];
    let pos = cartesianPositionCache.get(rec.key);
    if (!pos) {
      pos = Cesium.Cartesian3.fromDegrees(rec.lng, rec.lat, rec.height + 7);
      if (rec.height !== 0 || !terrainProvider) {
        cartesianPositionCache.set(rec.key, pos);
      }
    }

    const visual = markerVisual(rec.feature);
    billboardCollection.add({
      position: pos,
      image: landslideIcon(visual.kind, visual.color),
      verticalOrigin: Cesium.VerticalOrigin.CENTER,
      scale: 0.95,
      scaleByDistance: sharedNearFarScalar,
      id: rec.feature
    });
  }

  if (focus) focusCesiumOnMap(true);
  viewer.scene.requestRender();
  set3dStatus("", false);
}

function set3dStatus(message, visible) { const status=document.getElementById("three-d-status"); if(!status) return; status.textContent=message; status.hidden=!visible; }
function focusCesiumOnMap(animate) {
  if(!viewer||!map) return;
  const center=map.getCenter(), zoom=map.getZoom();
  const height=Math.max(3500,500000/Math.pow(2,Math.max(0,zoom-6)));
  const view={
    destination:Cesium.Cartesian3.fromDegrees(center.lng,center.lat,height),
    orientation:{heading:0, pitch:Cesium.Math.toRadians(-55), roll:0}
  };
  if(animate) viewer.camera.flyTo({...view, duration:1.0});
  else viewer.camera.setView(view);
}
function zoomCesium(direction) { if(!viewer||!document.getElementById("cesium-map").classList.contains("active"))return; const amount=Math.max(350,viewer.camera.positionCartographic.height*.42); if(direction>0)viewer.camera.zoomIn(amount);else viewer.camera.zoomOut(amount);viewer.scene.requestRender(); }
function leaveCesium() {
  const cesiumElement=document.getElementById("cesium-map");
  if(!viewer||!cesiumElement.classList.contains("active")) return;
  showLoading("RETURNING TO 2D VIEW", "Switching back to standard cartographic overview…", "VIEWPORT TOGGLE");
  let center=last2DView?.center||MAP_CONFIG.center, zoom=last2DView?.zoom??MAP_CONFIG.zoom;
  const canvas=viewer.canvas, ground=viewer.camera.pickEllipsoid(new Cesium.Cartesian2(canvas.clientWidth/2,canvas.clientHeight/2),viewer.scene.globe.ellipsoid);
  if(ground) { const location=Cesium.Cartographic.fromCartesian(ground), lat=Cesium.Math.toDegrees(location.latitude), lng=Cesium.Math.toDegrees(location.longitude); if(Number.isFinite(lat)&&Number.isFinite(lng)&&lat>=28&&lat<=35&&lng>=72&&lng<=82) center=[lat,lng]; }
  map.setView(center,zoom,{animate:false}); cesiumElement.classList.remove("active");document.getElementById("map").classList.remove("hidden");set3dStatus("",false);map.invalidateSize();
  hideLoading(250);
}

function initControls() {
  document.querySelectorAll(".hud-select-wrap select").forEach(el=>el.addEventListener("change",applyFilters));
  document.getElementById("reset-filters").addEventListener("click",()=>{
    ["district","year","activity","movement"].forEach(id=>document.getElementById(id).value="all");
    applyFilters();
  });
  document.getElementById("drawer-close").addEventListener("click",()=>document.getElementById("feature-drawer").classList.remove("open"));
  document.getElementById("cesium-zoom-in").addEventListener("click",()=>zoomCesium(1));
  document.getElementById("cesium-zoom-out").addEventListener("click",()=>zoomCesium(-1));

  // Layers Menu Toggle
  const toggle=document.getElementById("layers-toggle"), menu=document.getElementById("layers-menu");
  toggle.addEventListener("click",(e)=>{
    e.stopPropagation();
    const open=menu.hidden; menu.hidden=!open; toggle.setAttribute("aria-expanded",String(open));
  });
  document.addEventListener("click",(e)=>{
    if (!toggle.contains(e.target) && !menu.contains(e.target) && !menu.hidden) {
      menu.hidden = true;
      toggle.setAttribute("aria-expanded", "false");
    }
  });

  // Base map choice
  document.querySelectorAll("[data-layer-choice]").forEach(button=>button.addEventListener("click",()=>{
    const choice=button.dataset.layerChoice;
    document.querySelectorAll("[data-layer-choice]").forEach(b=>b.classList.remove("active"));
    button.classList.add("active");
    toggle.querySelector("span:nth-child(2)").textContent=button.textContent;
    if(choice==="3d") initCesium();
    else { leaveCesium(); switchBase(choice); }
  }));

  // Overlay Checkboxes
  const pointsToggle = document.getElementById("toggle-points");
  if (pointsToggle) {
    pointsToggle.addEventListener("change", (e) => {
      renderFeatures(false, false);
      if (billboardCollection) {
        billboardCollection.show = e.target.checked;
        viewer?.scene.requestRender();
      }
      const legend = document.getElementById("points-legend-card");
      if (legend) legend.style.display = e.target.checked ? "block" : "none";
    });
  }

  const polyToggle = document.getElementById("toggle-polygons");
  if (polyToggle) {
    polyToggle.addEventListener("change", (e) => togglePolygons(e.target.checked));
  }

  const roadsToggle = document.getElementById("toggle-roads");
  if (roadsToggle) {
    roadsToggle.addEventListener("change", (e) => toggleRoads(e.target.checked));
  }

  const commToggle = document.getElementById("toggle-community");
  if (commToggle) {
    commToggle.addEventListener("change", (e) => {
      if (!communityReportsLayer) return;
      const currentDist = document.getElementById("district")?.value || "all";
      renderCommunityReports(currentDist);
      if (e.target.checked) {
        if (!map.hasLayer(communityReportsLayer)) map.addLayer(communityReportsLayer);
      } else {
        if (map.hasLayer(communityReportsLayer)) map.removeLayer(communityReportsLayer);
      }
    });
  }

  // Environmental Radio selection
  document.querySelectorAll('input[name="env-layer-choice"]').forEach(radio => {
    radio.addEventListener("change", (e) => {
      toggleEnvironmental(e.target.value, currentEnvOpacity);
    });
  });

  // Opacity slider
  const opSlider = document.getElementById("env-opacity-slider");
  const opVal = document.getElementById("env-opacity-val");
  if (opSlider) {
    opSlider.addEventListener("input", (e) => {
      const val = parseInt(e.target.value, 10);
      currentEnvOpacity = val / 100;
      if (opVal) opVal.textContent = `${val}%`;
      if (environmentalLayer) environmentalLayer.setOpacity(currentEnvOpacity);
      if (cesiumEnvLayer) {
        cesiumEnvLayer.alpha = currentEnvOpacity;
        viewer?.scene.requestRender();
      }
    });
  }
}
 
// --- COMMUNITY REPORTS MODULE ---
let communityReportsLayer = null;
let cachedCommunityReportsData = null;
let reportPinMarker = null;

function renderCommunityReports(district = "all") {
  if (!communityReportsLayer || !cachedCommunityReportsData) return;
  communityReportsLayer.clearLayers();
  const commToggle = document.getElementById("toggle-community");
  if (commToggle && !commToggle.checked) return;

  let distFeature = null, distBounds = null;
  if (district && district !== "all" && boundaryData?.features) {
    distFeature = boundaryData.features.find(f => districtName(f).toLowerCase() === district.toLowerCase());
    if (distFeature) distBounds = L.geoJSON(distFeature).getBounds();
  }

  (cachedCommunityReportsData.features || []).forEach(feature => {
    const [lng, lat] = feature.geometry.coordinates;
    const props = feature.properties || {};

    if (district && district !== "all") {
      const repDist = (props.district || "").toLowerCase();
      if (repDist !== district.toLowerCase() && distFeature && !isPointInDistrict(lat, lng, distFeature, distBounds)) return;
      if (distFeature && !isPointInDistrict(lat, lng, distFeature, distBounds)) return;
    }

    const icon = L.divIcon({
      className: "community-marker-icon",
      html: `<div class="community-beacon-pin" title="Citizen Report: ${props.movement_type} (${props.severity})"><span class="beacon-pulse"></span><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg></div>`,
      iconSize: [28, 28],
      iconAnchor: [14, 14]
    });

    const marker = L.marker([lat, lng], { icon: icon });
    const photoHtml = props.photo_url ? 
      `<div class="popup-photo-wrap"><img src="${props.photo_url}" alt="Reported Landslide" class="popup-report-photo"></div>` : "";

    const popupContent = `
      <div class="community-popup">
        <div class="popup-header-tag">
          <span class="popup-severity severity-${(props.severity || 'moderate').toLowerCase()}">${(props.severity || 'MODERATE').toUpperCase()}</span>
          <span class="popup-id">${props.id || 'REPORT'}</span>
        </div>
        <h4 class="popup-title">${props.movement_type || 'Landslide'} &bull; ${props.district}</h4>
        ${photoHtml}
        <p class="popup-desc">${props.description || 'Citizen-reported slope instability incident.'}</p>
        <div class="popup-meta-row">
          <span><svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:inline;vertical-align:middle;margin-right:3px;"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>${props.incident_date || 'Recent'}</span>
          <span><svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:inline;vertical-align:middle;margin-right:3px;"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>${props.reporter_name || 'Anonymous'}</span>
        </div>
        <div class="popup-coords-row"><svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:inline;vertical-align:middle;margin-right:3px;"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>${lat.toFixed(4)}° N, ${lng.toFixed(4)}° E</div>
      </div>
    `;
    marker.bindPopup(popupContent, { maxWidth: 280, className: "community-leaflet-popup" });
    communityReportsLayer.addLayer(marker);
  });
}

async function loadCommunityReports() {
  try {
    const data = await fetchJSON("/api/reports");
    cachedCommunityReportsData = data;
    if (!communityReportsLayer) {
      communityReportsLayer = L.markerClusterGroup({
        maxClusterRadius: 35,
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: false
      });
      const commToggle = document.getElementById("toggle-community");
      if (!commToggle || commToggle.checked) {
        communityReportsLayer.addTo(map);
      }
    }
    const currentDist = document.getElementById("district")?.value || "all";
    renderCommunityReports(currentDist);
  } catch (err) {
    console.warn("Failed to load community reports", err);
  }
}

// --- DATASET EXPORT MODULE ---
function initExportModule() {
  const modal = document.getElementById("export-modal");
  const openBtn = document.getElementById("open-export-modal");
  const closeBtn = document.getElementById("export-modal-close");
  const cancelBtn = document.getElementById("export-cancel-btn");
  const triggerBtn = document.getElementById("export-trigger-btn");
  const districtSelect = document.getElementById("export-district-select");
  const yearSelect = document.getElementById("export-year-select");
  const previewCount = document.getElementById("export-preview-count");

  function openModal() {
    if (districtSelect && districtSelect.options.length <= 1) {
      const districts = [...new Set(allFeatures.map(f => p(f, "district")).filter(d => d && d !== "Not recorded in source"))].sort();
      districts.forEach(dist => {
        const opt = document.createElement("option");
        opt.value = dist.toLowerCase();
        opt.textContent = dist;
        districtSelect.appendChild(opt);
      });
    }

    if (yearSelect && yearSelect.options.length <= 1) {
      const years = [...new Set(allFeatures.map(f => p(f, "year")).filter(y => y && y !== "Not recorded in source"))].sort();
      years.forEach(yr => {
        const opt = document.createElement("option");
        opt.value = yr.toLowerCase();
        opt.textContent = yr;
        yearSelect.appendChild(opt);
      });
    }

    const currentDist = document.getElementById("district")?.value || "all";
    const currentYr = document.getElementById("year")?.value || "all";
    if (districtSelect) districtSelect.value = currentDist.toLowerCase();
    if (yearSelect) yearSelect.value = currentYr.toLowerCase();

    updateCount();
    modal?.removeAttribute("hidden");
  }

  function closeModal() {
    modal?.setAttribute("hidden", "");
  }

  function updateCount() {
    const selDist = districtSelect?.value || "all";
    const selYr = yearSelect?.value || "all";

    const count = allFeatures.filter(f => {
      const fDist = p(f, "district", "").toLowerCase();
      const fYr = p(f, "year", "").toLowerCase();
      if (selDist !== "all" && fDist !== selDist) return false;
      if (selYr !== "all" && fYr !== selYr) return false;
      return true;
    }).length;

    if (previewCount) {
      previewCount.textContent = `Ready to download: ${count.toLocaleString()} landslide records`;
    }
  }

  openBtn?.addEventListener("click", openModal);
  closeBtn?.addEventListener("click", closeModal);
  cancelBtn?.addEventListener("click", closeModal);

  modal?.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });

  districtSelect?.addEventListener("change", updateCount);
  yearSelect?.addEventListener("change", updateCount);

  document.querySelectorAll('input[name="export-format"]').forEach(radio => {
    radio.addEventListener("change", (e) => {
      document.querySelectorAll(".format-choice").forEach(fc => fc.classList.remove("active"));
      e.target.closest(".format-choice")?.classList.add("active");
    });
  });

  triggerBtn?.addEventListener("click", () => {
    const dist = districtSelect?.value || "all";
    const yr = yearSelect?.value || "all";
    const fmt = document.querySelector('input[name="export-format"]:checked')?.value || "csv";

    if (triggerBtn) {
      triggerBtn.disabled = true;
      triggerBtn.innerHTML = `<span>⏳ Preparing Export…</span>`;
    }

    const downloadUrl = `/api/export?district=${encodeURIComponent(dist)}&year=${encodeURIComponent(yr)}&format=${encodeURIComponent(fmt)}`;
    window.location.href = downloadUrl;

    setTimeout(() => {
      if (triggerBtn) {
        triggerBtn.disabled = false;
        triggerBtn.innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="display:inline-block;vertical-align:middle;margin-right:4px;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg><span>Download Dataset</span>`;
      }
      closeModal();
    }, 1500);
  });
}

window.addEventListener("resize",()=>map?.invalidateSize());
