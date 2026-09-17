"use strict";
let map, markerLayer, allFeatures = [], filteredFeatures = [], selectedMarker, boundaryData, districtLayer, maskLayer, viewer, terrainProvider, billboardCollection, terrainRenderVersion = 0, last2DView, cesiumDistrictDataSource, cesiumBoundaryVersion = 0;
const MAP_CONFIG = { center:[31.75,77.1], zoom:8, minZoom:6, maxZoom:18 };
const layers = {};
document.addEventListener("DOMContentLoaded", init);

async function init() {
  initMap(); initControls();
  try {
    const [inventory, boundaries] = await Promise.all([fetchJSON("/api/landslides"), fetchJSON("/api/district-boundaries")]);
    allFeatures = inventory.features.filter(validFeature); filteredFeatures = [...allFeatures]; boundaryData = boundaries;
    populateFilters(); renderDistrictBoundaries(); renderFeatures(true, false); document.getElementById("map-loading").classList.add("loaded");

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
  filteredFeatures.forEach(feature => { const [lng,lat]=feature.geometry.coordinates.map(Number); if (!Number.isFinite(lat)||!Number.isFinite(lng)) return; const marker=L.marker([lat,lng],{icon:leafletIcon(feature),keyboard:false,riseOnHover:true}); marker.on("click",()=>{ highlight(marker,feature); drawer(feature,lat,lng); }); markers.push(marker); positions.push([lat,lng]); });
  markerLayer.addLayers(markers);
  document.getElementById("visible-count").textContent=filteredFeatures.length.toLocaleString("en-IN"); if(fit&&positions.length) map.fitBounds(L.latLngBounds(positions),{padding:[60,60],maxZoom:13});
  if (viewer) renderCesiumPoints(focus3d);
}
function markerVisual(feature) { const activity=p(feature,"activity","").toLowerCase(), movement=p(feature,"movement","").toLowerCase(); if(activity.includes("active")) return {kind:"active",color:"#38bdf8"}; if(movement.includes("fall")) return {kind:"fall",color:"#f59e0b"}; if(movement.includes("flow")) return {kind:"flow",color:"#a855f7"}; if(movement.includes("slide")) return {kind:"slide",color:"#10b981"}; if(movement.includes("debris")) return {kind:"debris",color:"#ef4444"}; return {kind:"record",color:"#10b981"}; }
const iconCache={};
function landslideIcon(kind,color) { const cacheKey=`${kind}-${color}`; if(iconCache[cacheKey]) return iconCache[cacheKey]; const glyph={active:"●",fall:"◆",flow:"≈",slide:"▲",debris:"⬟",record:"●"}[kind]||"●"; const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 22 22"><circle cx="11" cy="11" r="9.5" fill="#071f19" fill-opacity=".82" stroke="white" stroke-width="1.4"/><text x="11" y="15" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="bold" fill="${color}">${glyph}</text></svg>`; iconCache[cacheKey]=`data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`; return iconCache[cacheKey]; }
function leafletIcon(feature) { const visual=markerVisual(feature); return L.divIcon({className:"landslide-leaflet-icon",html:`<img alt="" src="${landslideIcon(visual.kind,visual.color)}">`,iconSize:[22,22],iconAnchor:[11,11]}); }
function highlight(marker, feature) { if(selectedMarker) selectedMarker.getElement()?.classList.remove("selected-landslide-icon"); marker.feature=feature; marker.getElement()?.classList.add("selected-landslide-icon"); selectedMarker=marker; }
function drawer(feature,lat,lng) { const props=feature.properties||{}, set=(id,value)=>document.getElementById(id).textContent=value; set("drawer-title",property(props,["id_land","id"],"Mapped Feature")); set("drawer-district",p(feature,"district")); set("drawer-year",p(feature,"year")); set("drawer-activity",p(feature,"activity")); set("drawer-movement",p(feature,"movement")); set("drawer-material",p(feature,"material")); set("drawer-style",property(props,["style","STYLE"])); const road=Number(props.distance_to_road_m); set("drawer-road-distance",Number.isFinite(road)?`${road.toFixed(1)} m`:"Not recorded in source"); set("drawer-trigger",property(props,["triggering","trigger" ],"Not recorded in source")); set("drawer-geology",property(props,["geology"],"Not recorded in source")); set("drawer-hydrology",property(props,["hydrologic","hydrology"],"Not recorded in source")); set("drawer-landuse",property(props,["landuse_la","landuse"],"Not recorded in source")); set("drawer-coords",`${lat.toFixed(5)}° N, ${lng.toFixed(5)}° E`); document.getElementById("feature-drawer").classList.add("open"); }
function districtName(feature) { return property(feature?.properties,["district","name","lgd_districtname"],""); }
function populateFilters() { const districts=[...new Set((boundaryData?.features||[]).map(districtName).filter(Boolean))].sort((a,b)=>a.localeCompare(b)); populate("district",districts); populate("year",unique("year").sort().reverse()); populate("activity",unique("activity")); populate("movement",unique("movement")); document.getElementById("district-count").textContent=districts.length.toLocaleString("en-IN"); }
function unique(field) { return [...new Set(allFeatures.map(f=>p(f,field,"")).filter(Boolean))].sort((a,b)=>a.localeCompare(b,undefined,{numeric:true})); }
function populate(id, values) { const el=document.getElementById(id); values.forEach(value=>el.add(new Option(value,value))); }
function applyFilters() { const query=id=>document.getElementById(id).value; const district=query("district"), year=query("year"), activity=query("activity"), movement=query("movement"); filteredFeatures=allFeatures.filter(f=>(district==="all"||p(f,"district").toLowerCase()===district.toLowerCase())&&(year==="all"||p(f,"year")===year)&&(activity==="all"||p(f,"activity").toLowerCase()===activity.toLowerCase())&&(movement==="all"||p(f,"movement").toLowerCase()===movement.toLowerCase())); isolateDistrict(district); renderFeatures(district==="all",true); }
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
async function initCesium() {
  const mapCenter=map.getCenter(); last2DView={center:[mapCenter.lat,mapCenter.lng],zoom:map.getZoom()};
  if(viewer) { document.getElementById("cesium-map").classList.add("active"); document.getElementById("map").classList.add("hidden"); focusCesiumOnMap(true); return; }
  const target=document.getElementById("cesium-map"); target.classList.add("active"); document.getElementById("map").classList.add("hidden");
  const token=window.HIMA_CONFIG?.cesiumIonToken;
  if(token) Cesium.Ion.defaultAccessToken=token;
  // OSM imagery deliberately needs no Cesium/API key and avoids a blue globe.
  const osm=new Cesium.UrlTemplateImageryProvider({url:"https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",subdomains:["a","b","c"],credit:"© OpenStreetMap contributors"});
  // Cesium 1.122 uses baseLayer; imageryProvider is ignored and creates the blue default globe.
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
  viewer.scene.globe.depthTestAgainstTerrain=true; await renderCesiumPoints(false);
  viewer.screenSpaceEventHandler.setInputAction(movement=>{ const picked=viewer.scene.pick(movement.position); const feature=picked?.id; if(feature?.type==="Feature") { const [lng,lat]=feature.geometry.coordinates; drawer(feature,Number(lat),Number(lng)); } },Cesium.ScreenSpaceEventType.LEFT_CLICK);
}
async function renderCesiumPoints(focus=false) {
  if(!viewer) return; const version=++terrainRenderVersion;
  if(billboardCollection) viewer.scene.primitives.remove(billboardCollection);
  billboardCollection=viewer.scene.primitives.add(new Cesium.BillboardCollection());
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
function initControls() { document.querySelectorAll(".hud-select-wrap select").forEach(el=>el.addEventListener("change",applyFilters)); document.getElementById("reset-filters").addEventListener("click",()=>{["district","year","activity","movement"].forEach(id=>document.getElementById(id).value="all");applyFilters();}); document.getElementById("drawer-close").addEventListener("click",()=>document.getElementById("feature-drawer").classList.remove("open")); document.getElementById("cesium-zoom-in").addEventListener("click",()=>zoomCesium(1));document.getElementById("cesium-zoom-out").addEventListener("click",()=>zoomCesium(-1)); const toggle=document.getElementById("layers-toggle"), menu=document.getElementById("layers-menu"); toggle.addEventListener("click",()=>{const open=menu.hidden;menu.hidden=!open;toggle.setAttribute("aria-expanded",String(open));}); document.querySelectorAll("[data-layer-choice]").forEach(button=>button.addEventListener("click",()=>{const choice=button.dataset.layerChoice;menu.hidden=true;toggle.setAttribute("aria-expanded","false");toggle.querySelector("span:nth-child(2)").textContent=button.textContent; if(choice==="3d") initCesium(); else { leaveCesium(); switchBase(choice); }})); }
window.addEventListener("resize",()=>map?.invalidateSize());
