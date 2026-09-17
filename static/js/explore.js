"use strict";
let map, markerLayer, allFeatures = [], filteredFeatures = [], selectedMarker, boundaryData, districtLayer, maskLayer, viewer, terrainProvider, billboardCollection, terrainRenderVersion = 0, last2DView, cesiumDistrictDataSource, cesiumBoundaryVersion = 0;
let roadLayer = null, polygonLayer = null, environmentalLayer = null, environmentalMeta = null;
let cesiumRoadsDataSource = null, cesiumPolygonsDataSource = null, cesiumEnvLayer = null;
let cachedRoadsGeoJSON = null;
let currentEnvChoice = "none", currentEnvOpacity = 0.8;
const MAP_CONFIG = { center:[31.75,77.1], zoom:8, minZoom:6, maxZoom:18 };
const layers = {};
document.addEventListener("DOMContentLoaded", init);

async function init() {
  initMap(); initControls();
  initExportModule();
  try {
    const [inventory, boundaries] = await Promise.all([fetchJSON("/api/landslides"), fetchJSON("/api/district-boundaries")]);
    allFeatures = inventory.features.filter(validFeature); filteredFeatures = [...allFeatures]; boundaryData = boundaries;
    populateFilters(); renderDistrictBoundaries(); renderFeatures(true, false);
    loadCommunityReports();
    document.getElementById("map-loading").classList.add("loaded");

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
  } catch (error) { console.error(error); document.getElementById("map-status").textContent = "DATASTREAM OFFLINE — RETRY"; }
}

async function fetchJSON(url) { const response = await fetch(url, {headers:{Accept:"application/json"}}); if (!response.ok) throw Error(`HTTP ${response.status}`); return response.json(); }

function initMap() {
  map = L.map("map", {center:MAP_CONFIG.center, zoom:MAP_CONFIG.zoom, minZoom:MAP_CONFIG.minZoom, maxZoom:MAP_CONFIG.maxZoom, zoomControl:false, preferCanvas:true});
  L.control.zoom({position:"bottomright"}).addTo(map);
  layers.standard = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {maxZoom:19, attribution:"© OpenStreetMap contributors"});
  layers.satellite = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {maxZoom:18, attribution:"Tiles © Esri"});
  layers.terrain = L.tileLayer("https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png", {maxZoom:17, attribution:"© OpenTopoMap © OpenStreetMap contributors"});
  layers.standard.addTo(map); markerLayer = L.markerClusterGroup({chunkedLoading:true,chunkInterval:25,chunkDelay:10,removeOutsideVisibleBounds:true,spiderfyOnMaxZoom:false,maxClusterRadius:48,showCoverageOnHover:false}).addTo(map);
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

function applyFilters() {
  const query=id=>document.getElementById(id).value;
  const district=query("district"), year=query("year"), activity=query("activity"), movement=query("movement");
  filteredFeatures=allFeatures.filter(f=>(district==="all"||p(f,"district").toLowerCase()===district.toLowerCase())&&(year==="all"||p(f,"year")===year)&&(activity==="all"||p(f,"activity").toLowerCase()===activity.toLowerCase())&&(movement==="all"||p(f,"movement").toLowerCase()===movement.toLowerCase()));
  isolateDistrict(district);
  renderFeatures(district==="all",true);
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
function switchBase(name) { Object.values(layers).forEach(layer=>map.removeLayer(layer)); layers[name].addTo(map); }

// --- ARCGIS OVERLAY MANAGEMENT ---
async function toggleRoads(visible) {
  updateCesiumRoads(visible);
  if (!visible) {
    if (roadLayer && map.hasLayer(roadLayer)) map.removeLayer(roadLayer);
    return;
  }
  if (!cachedRoadsGeoJSON) {
    document.getElementById("map-status").textContent = "FETCHING MANDI ROAD NETWORK…";
    document.getElementById("map-loading").classList.remove("loaded");
    try {
      cachedRoadsGeoJSON = await fetchJSON("/api/roads");
    } catch (e) {
      console.error("Failed to load roads", e);
      return;
    } finally {
      document.getElementById("map-loading").classList.add("loaded");
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

  document.getElementById("map-status").textContent = "FETCHING HAZARD ZONE POLYGONS…";
  document.getElementById("map-loading").classList.remove("loaded");
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
    document.getElementById("map-loading").classList.add("loaded");
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

  if (!environmentalMeta) {
    try {
      const res = await fetchJSON("/api/environmental-layers");
      environmentalMeta = res.layers || {};
    } catch (e) {
      console.error("Failed to load environmental metadata", e);
      return;
    }
  }

  const meta = environmentalMeta[choice];
  if (!meta) return;

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
  if(viewer) {
    document.getElementById("cesium-map").classList.add("active");
    document.getElementById("map").classList.add("hidden");
    focusCesiumOnMap(true);
    await syncCesiumAllOverlays();
    return;
  }
  const target=document.getElementById("cesium-map"); target.classList.add("active"); document.getElementById("map").classList.add("hidden");
  const token=window.HIMA_CONFIG?.cesiumIonToken;
  if(token) Cesium.Ion.defaultAccessToken=token;
  const osm=new Cesium.UrlTemplateImageryProvider({url:"https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",subdomains:["a","b","c"],credit:"© OpenStreetMap contributors"});
  viewer=new Cesium.Viewer("cesium-map",{baseLayer:new Cesium.ImageryLayer(osm),baseLayerPicker:false,geocoder:false,animation:false,timeline:false,homeButton:false,sceneModePicker:false,navigationHelpButton:false,requestRenderMode:true,maximumRenderTimeChange:Infinity});
  const selectedDistrict=document.getElementById("district").value; if(selectedDistrict!=="all")updateCesiumDistrictBoundary(boundaryData?.features?.find(feature=>districtName(feature).toLowerCase()===selectedDistrict.toLowerCase()));
  focusCesiumOnMap(false);
  set3dStatus("LOADING SATELLITE IMAGERY & TERRAIN…", true);
  if(token) {
    try {
      const [satellite, terrain] = await Promise.all([
        Cesium.createWorldImageryAsync({style:Cesium.IonWorldImageryStyle.AERIAL}),
        Cesium.createWorldTerrainAsync({requestVertexNormals:true})
      ]);
      viewer.imageryLayers.removeAll(); viewer.imageryLayers.addImageryProvider(satellite);
      terrainProvider=terrain; viewer.terrainProvider=terrain;
    } catch(error) { console.warn("Cesium Ion imagery/terrain could not load; retaining OSM fallback.",error); }
  } else console.warn("No CESIUM_ION_TOKEN provided; retaining OSM fallback.");
  viewer.scene.globe.depthTestAgainstTerrain=true;
  await renderCesiumPoints(false);
  await syncCesiumAllOverlays();

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

async function renderCesiumPoints(focus=false) {
  if(!viewer) return; const version=++terrainRenderVersion;
  if(billboardCollection) viewer.scene.primitives.remove(billboardCollection);
  billboardCollection=viewer.scene.primitives.add(new Cesium.BillboardCollection());
  const showPoints = document.getElementById("toggle-points") ? document.getElementById("toggle-points").checked : true;
  billboardCollection.show = showPoints;
  const records=filteredFeatures.map(feature=>({feature, coordinates:feature.geometry.coordinates.map(Number)})).filter(record=>Number.isFinite(record.coordinates[0])&&Number.isFinite(record.coordinates[1]));
  const terrainPositions=records.map(record=>Cesium.Cartographic.fromDegrees(record.coordinates[0],record.coordinates[1]));
  set3dStatus(`PROJECTING ${records.length.toLocaleString("en-IN")} POINTS 7 m ABOVE TERRAIN…`, true);
  if(terrainProvider) { try { await Cesium.sampleTerrainMostDetailed(terrainProvider,terrainPositions); } catch(error) { console.warn("Terrain height sampling failed; rendering ellipsoid-height fallback.",error); } }
  if(version!==terrainRenderVersion) return;
  records.forEach((record,index)=>{ const surfaceHeight=Number.isFinite(terrainPositions[index].height)?terrainPositions[index].height:0; const visual=markerVisual(record.feature); billboardCollection.add({position:Cesium.Cartesian3.fromRadians(terrainPositions[index].longitude,terrainPositions[index].latitude,surfaceHeight+7),image:landslideIcon(visual.kind,visual.color),verticalOrigin:Cesium.VerticalOrigin.CENTER,scale:0.95,scaleByDistance:new Cesium.NearFarScalar(1000,1.1,150000,.52),id:record.feature}); });
  if(focus) focusCesiumOnMap(true); viewer.scene.requestRender(); set3dStatus("", false);
}

function set3dStatus(message, visible) { const status=document.getElementById("three-d-status"); if(!status) return; status.textContent=message; status.hidden=!visible; }
function focusCesiumOnMap(animate) { if(!viewer||!map) return; const center=map.getCenter(), zoom=map.getZoom(); const height=Math.max(3500,500000/Math.pow(2,Math.max(0,zoom-6))); const view={destination:Cesium.Cartesian3.fromDegrees(center.lng,center.lat,height),orientation:{heading:0,pitch:-Cesium.Math.PI_OVER_TWO,roll:0}}; if(animate)viewer.camera.flyTo({...view,duration:.45});else viewer.camera.setView(view); }
function zoomCesium(direction) { if(!viewer||!document.getElementById("cesium-map").classList.contains("active"))return; const amount=Math.max(350,viewer.camera.positionCartographic.height*.42); if(direction>0)viewer.camera.zoomIn(amount);else viewer.camera.zoomOut(amount);viewer.scene.requestRender(); }
function leaveCesium() {
  const cesiumElement=document.getElementById("cesium-map");
  if(!viewer||!cesiumElement.classList.contains("active")) return;
  let center=last2DView?.center||MAP_CONFIG.center, zoom=last2DView?.zoom??MAP_CONFIG.zoom;
  const canvas=viewer.canvas, ground=viewer.camera.pickEllipsoid(new Cesium.Cartesian2(canvas.clientWidth/2,canvas.clientHeight/2),viewer.scene.globe.ellipsoid);
  if(ground) { const location=Cesium.Cartographic.fromCartesian(ground), lat=Cesium.Math.toDegrees(location.latitude), lng=Cesium.Math.toDegrees(location.longitude); if(Number.isFinite(lat)&&Number.isFinite(lng)&&lat>=28&&lat<=35&&lng>=72&&lng<=82) center=[lat,lng]; }
  map.setView(center,zoom,{animate:false}); cesiumElement.classList.remove("active");document.getElementById("map").classList.remove("hidden");set3dStatus("",false);map.invalidateSize();
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
let reportPinMarker = null;

async function loadCommunityReports() {
  try {
    const data = await fetchJSON("/api/reports");
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
    } else {
      communityReportsLayer.clearLayers();
    }

    (data.features || []).forEach(feature => {
      const [lng, lat] = feature.geometry.coordinates;
      const props = feature.properties || {};

      const icon = L.divIcon({
        className: "community-marker-icon",
        html: `<div class="community-beacon-pin" title="Citizen Report: ${props.movement_type} (${props.severity})"><span class="beacon-pulse"></span>📷</div>`,
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
            <span>📅 ${props.incident_date || 'Recent'}</span>
            <span>👤 ${props.reporter_name || 'Anonymous'}</span>
          </div>
          <div class="popup-coords-row">📍 ${lat.toFixed(4)}° N, ${lng.toFixed(4)}° E</div>
        </div>
      `;
      marker.bindPopup(popupContent, { maxWidth: 280, className: "community-leaflet-popup" });
      communityReportsLayer.addLayer(marker);
    });
  } catch (err) {
    console.warn("Failed to load community reports", err);
  }
}
  const commToggle = document.getElementById("toggle-community");
  commToggle?.addEventListener("change", (e) => {
    if (!communityReportsLayer) return;
    if (e.target.checked) {
      map.addLayer(communityReportsLayer);
    } else {
      map.removeLayer(communityReportsLayer);
    }
  });
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
        triggerBtn.innerHTML = `<span>📥 Download Dataset</span>`;
      }
      closeModal();
    }, 1500);
  });
}

window.addEventListener("resize",()=>map?.invalidateSize());
