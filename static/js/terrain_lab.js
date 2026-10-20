"use strict";
/**
 * ============================================================================
 * HIMA-LENS: 3D Himalayan Alpine Terrain & Landslide Kinematics Showcase
 * Awwwards "Site of the Day" Quality Architecture
 *
 * Inspired by Swiss Alpine Club, Moncler Grenoble, and EnduroSat Minimalism
 * Built in TypeScript (ES2020) with Three.js WebGL & GSAP ScrollTrigger
 * ============================================================================
 */
class HimalayanTerrainShowcase {
    constructor() {
        this.canvas = null;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.composer = null;
        this.clock = null;
        // 3D Scene Elements
        this.terrainGroup = null;
        this.terrainMesh = null;
        this.terrainMaterial = null;
        this.valleyRiverMesh = null;
        this.highwayRibbon = null;
        this.shearFaultMesh = null;
        this.mistParticles = null;
        this.sunLight = null;
        // Interactive Pins
        this.hotspotPins = [];
        this.pinDomElements = [];
        // State & Mouse Tracking
        this.currentChapter = 0;
        this.mouseX = 0;
        this.mouseY = 0;
        this.targetMouseX = 0;
        this.targetMouseY = 0;
        this.isUserOrbiting = false;
        this.dragStartX = 0;
        this.dragStartY = 0;
        this.orbitAngleY = 0;
        this.orbitAngleX = 0;
        // Chapters Configuration
        this.chapters = [
            {
                id: 0,
                kicker: "01 / HIGH HIMALAYAN SUMMITS",
                title: "The Living Massif.",
                subtext: "Towering, active, and under unrelenting tectonic compression. Himachal's alpine ridges rise above 6,000 meters, shaped by glacial cirques and extreme freeze-thaw weathering.",
                camPos: { x: 0, y: 16, z: 28 },
                targetPos: { x: 0, y: 4, z: 0 },
                elevation: "5,840 M",
                slopeAngle: "62° ARÊTE",
                status: "TECTONIC CREEP",
                activeFeature: "HIGHWAY CORRIDOR NH-21"
            },
            {
                id: 1,
                kicker: "02 / DAYLIGHTING CLEAVAGE",
                title: "Where Rock Meets Gravity.",
                subtext: "Steep highway cuts expose daylighting metamorphic bedding joints. When joint dip angles align with the valley slope, colossal rock masses become frictionally unstable.",
                camPos: { x: -8, y: 7.5, z: 14 },
                targetPos: { x: 1.5, y: 3.2, z: 2 },
                elevation: "2,910 M",
                slopeAngle: "46° DAYLIGHTING",
                status: "CRITICAL SHEAR",
                activeFeature: "SLIP SURFACE DETECTED"
            },
            {
                id: 2,
                kicker: "03 / CLOUDBURST INFILTRATION",
                title: "The Water Trigger.",
                subtext: "Monsoon precipitation fluxes exceed 40 mm per hour. Water infiltrates deep colluvial fissures, spiking pore-water pressure and dissolving effective shear resistance along the slip plane.",
                camPos: { x: 9.5, y: 6.2, z: 12 },
                targetPos: { x: -2.0, y: 2.5, z: -1 },
                elevation: "2,150 M",
                slopeAngle: "38° COLLUVIUM",
                status: "SATURATION FLUX",
                activeFeature: "PORE PRESSURE SURGE"
            },
            {
                id: 3,
                kicker: "04 / VALLEY HUMAN LIFELINE",
                title: "Protecting the Corridor.",
                subtext: "At the valley floor, the national highway corridor connects communities, hydroelectric projects, and transit lifelines. Automated sensors deliver early warning before failure reaches the road.",
                camPos: { x: 0.5, y: 3.5, z: 9.5 },
                targetPos: { x: 0, y: 0.5, z: 0 },
                elevation: "1,220 M",
                slopeAngle: "14° VALLEY FLOOR",
                status: "OPERATIONAL MONITOR",
                activeFeature: "EARLY WARNING CONFIRMED"
            }
        ];
        this.init();
    }
    init() {
        this.canvas = document.getElementById("terrain-webgl-canvas");
        if (!this.canvas || typeof THREE === "undefined") {
            console.error("Three.js or canvas element not available");
            return;
        }
        this.clock = new THREE.Clock();
        this.setupRendererAndCamera();
        this.setupPostProcessing();
        this.setupAtmosphericLighting();
        this.generateAlpineMassifMesh();
        this.createValleyRiverAndCorridor();
        this.createActiveShearPlane();
        this.createAtmosphericMistParticles();
        this.bindEvents();
        this.setupGsapScrollScrubbing();
        this.updateTelemetryHUD(0);
        this.animate();
    }
    setupRendererAndCamera() {
        const w = window.innerWidth;
        const h = window.innerHeight;
        this.scene = new THREE.Scene();
        // Deep alpine twilight navy-black background
        this.scene.background = new THREE.Color(0x020a08);
        this.scene.fog = new THREE.FogExp2(0x020a08, 0.018);
        this.camera = new THREE.PerspectiveCamera(40, w / h, 0.1, 1000);
        this.camera.position.set(this.chapters[0].camPos.x, this.chapters[0].camPos.y, this.chapters[0].camPos.z);
        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            antialias: true,
            alpha: true,
            powerPreference: "high-performance"
        });
        this.renderer.setSize(w, h);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.25;
    }
    setupPostProcessing() {
        const w = window.innerWidth;
        const h = window.innerHeight;
        if (THREE.EffectComposer && THREE.RenderPass && THREE.UnrealBloomPass) {
            this.composer = new THREE.EffectComposer(this.renderer);
            const renderPass = new THREE.RenderPass(this.scene, this.camera);
            this.composer.addPass(renderPass);
            // Refined High-End Optical Bloom (soft luminescence on contour lasers & ridge crests)
            const bloom = new THREE.UnrealBloomPass(new THREE.Vector2(w, h), 0.85, // Strength
            0.5, // Radius
            0.68 // Threshold
            );
            this.composer.addPass(bloom);
        }
    }
    setupAtmosphericLighting() {
        // Cool alpine ambient shadow light
        const ambient = new THREE.AmbientLight(0x08221b, 1.6);
        this.scene.add(ambient);
        // Low golden-hour Sun over Himalayan peaks
        this.sunLight = new THREE.DirectionalLight(0xffeedd, 3.2);
        this.sunLight.position.set(30, 22, -20);
        this.sunLight.castShadow = true;
        this.scene.add(this.sunLight);
        // Soft cyan valley up-bounce light
        const bounce = new THREE.DirectionalLight(0x2dd4bf, 0.9);
        bounce.position.set(-25, -10, 15);
        this.scene.add(bounce);
    }
    /**
     * Procedural High-Relief Himalayan Mountain Massif
     * Uses Ridged Multi-Fractal Brownian Motion (fBm) to generate sharp razor-crested alpine arêtes,
     * steep metamorphic rock faces, and deep river gorges.
     */
    generateAlpineMassifMesh() {
        this.terrainGroup = new THREE.Group();
        const terrainSize = 65;
        const segments = 220; // High mesh resolution for razor-sharp ridge contours
        const geom = new THREE.PlaneGeometry(terrainSize, terrainSize, segments, segments);
        // Procedural Ridged Mountain Sculpting
        const pos = geom.attributes.position;
        for (let i = 0; i < pos.count; i++) {
            const x = pos.getX(i);
            const y = pos.getY(i);
            // Radial falloff to keep edges clean and contained
            const distFromCenter = Math.sqrt(x * x + y * y);
            const edgeMask = Math.max(0.0, Math.min(1.0, 1.0 - (distFromCenter / (terrainSize * 0.48))));
            const smoothEdge = edgeMask * edgeMask * (3.0 - 2.0 * edgeMask);
            // 1. Primary Tectonic Ridge (NW to SE strike, typical of the Himalayas)
            const ridge1 = Math.abs(Math.sin(x * 0.14 + y * 0.11)) * 5.5;
            const sharpPeak1 = (1.0 - Math.abs(Math.cos(x * 0.22 - y * 0.18))) * 4.2;
            // 2. High Alpine Pyramidal Horns & Arêtes
            const detail1 = (1.0 - Math.abs(Math.sin(x * 0.42 + y * 0.35))) * 2.2;
            const detail2 = Math.sin(x * 0.85 - y * 0.72) * 0.8;
            // 3. Glacial River Gorge Carve (Valley floor through center)
            const riverValleyDist = Math.abs(x * 0.65 - y * 0.35);
            const valleyDepth = Math.exp(-Math.pow(riverValleyDist, 2) / 18.0) * 4.8;
            // Combine into final elevation
            const elevation = ((ridge1 * sharpPeak1 * 0.35 + detail1 + detail2) - valleyDepth) * smoothEdge;
            pos.setZ(i, Math.max(-0.5, elevation));
        }
        geom.computeVertexNormals();
        // Custom High-End Alpine PBR & LiDAR Topographic Shader
        this.terrainMaterial = new THREE.ShaderMaterial({
            uniforms: {
                uTime: { value: 0 },
                uContourStep: { value: 1.4 },
                uLaserSweep: { value: 0.0 }
            },
            vertexShader: `
                varying vec3 vWorldPosition;
                varying vec3 vNormal;
                varying float vElevation;

                void main() {
                    vNormal = normalize(normalMatrix * normal);
                    vec4 worldPos = modelMatrix * vec4(position, 1.0);
                    vWorldPosition = worldPos.xyz;
                    vElevation = position.z;
                    gl_Position = projectionMatrix * viewMatrix * worldPos;
                }
            `,
            fragmentShader: `
                uniform float uTime;
                uniform float uContourStep;
                varying vec3 vWorldPosition;
                varying vec3 vNormal;
                varying float vElevation;

                void main() {
                    // Alpine Elevation & Geotechnical Stratigraphy Palette
                    vec3 valleyPine   = vec3(0.02, 0.14, 0.10);  // Dark sub-alpine forest
                    vec3 colluviumScree = vec3(0.12, 0.18, 0.17); // Colluvial regolith
                    vec3 graniteGneiss  = vec3(0.24, 0.29, 0.28); // Metamorphic bedrock cliffs
                    vec3 alpineSnow     = vec3(0.94, 0.98, 0.98); // High snow crests

                    // Elevation blend
                    vec3 rockColor = valleyPine;
                    if (vElevation > 0.6) rockColor = mix(valleyPine, colluviumScree, clamp((vElevation - 0.6) / 1.5, 0.0, 1.0));
                    if (vElevation > 2.2) rockColor = mix(colluviumScree, graniteGneiss, clamp((vElevation - 2.2) / 2.0, 0.0, 1.0));
                    if (vElevation > 4.2) rockColor = mix(graniteGneiss, alpineSnow, clamp((vElevation - 4.2) / 1.8, 0.0, 1.0));

                    // Slope steepness shading (steep rock sheds snow)
                    float slope = 1.0 - max(0.0, vNormal.z);
                    if (slope > 0.45 && vElevation > 4.2) {
                        rockColor = mix(rockColor, graniteGneiss, 0.75); // Steep bare cliff face
                    }

                    // Direct Sunlight & Shadow Diffuse
                    vec3 sunDir = normalize(vec3(0.65, 0.75, -0.45));
                    float diff = max(0.22, dot(vNormal, sunDir));

                    // Subtle, Elegant Topographic LiDAR Elevation Isolines (Thin, glowing cyan)
                    float contour = mod(vElevation, uContourStep);
                    float isoline = smoothstep(0.0, 0.05, contour) - smoothstep(0.05, 0.10, contour);

                    // Dynamic InSAR Radar Plane Wave (Traveling smoothly down the mountain)
                    float wave = sin(vWorldPosition.x * 0.25 + vWorldPosition.z * 0.25 - uTime * 2.2);
                    wave = smoothstep(0.96, 1.0, wave);

                    vec3 neonTeal = vec3(0.18, 0.83, 0.75);
                    vec3 finalSurface = mix(rockColor * diff, neonTeal, isoline * 0.38 + wave * 0.55);

                    gl_FragColor = vec4(finalSurface, 1.0);
                }
            `,
            side: THREE.DoubleSide
        });
        this.terrainMesh = new THREE.Mesh(geom, this.terrainMaterial);
        this.terrainMesh.rotation.x = -Math.PI / 2.2;
        this.terrainMesh.position.y = -1.2;
        this.terrainGroup.add(this.terrainMesh);
        this.scene.add(this.terrainGroup);
    }
    /**
     * Valley Floor River & Highway Corridor (NH-21 Lifeline)
     */
    createValleyRiverAndCorridor() {
        // Winding Valley Highway Path
        const highwayCurve = new THREE.CatmullRomCurve3([
            new THREE.Vector3(-22, -0.4, -14),
            new THREE.Vector3(-10, -0.2, -6),
            new THREE.Vector3(0, 0.1, 2),
            new THREE.Vector3(12, 0.3, 10),
            new THREE.Vector3(24, 0.6, 18)
        ]);
        const roadGeom = new THREE.TubeGeometry(highwayCurve, 80, 0.22, 8, false);
        const roadMat = new THREE.MeshBasicMaterial({
            color: 0x38bdf8, // Luminous highway corridor indicator
            transparent: true,
            opacity: 0.95
        });
        this.highwayRibbon = new THREE.Mesh(roadGeom, roadMat);
        this.terrainGroup.add(this.highwayRibbon);
        // River Bed Shimmer
        const riverGeom = new THREE.TubeGeometry(highwayCurve, 80, 0.55, 6, false);
        const riverMat = new THREE.MeshBasicMaterial({
            color: 0x092f25,
            transparent: true,
            opacity: 0.6
        });
        this.valleyRiverMesh = new THREE.Mesh(riverGeom, riverMat);
        this.valleyRiverMesh.position.y = -0.15;
        this.terrainGroup.add(this.valleyRiverMesh);
    }
    /**
     * Active Daylighting Landslide Shear Failure Plane
     * Displays a luminous planar rupture surface on a critical mountain cut-slope.
     */
    createActiveShearPlane() {
        const faultGeom = new THREE.PlaneGeometry(8.5, 5.5, 12, 12);
        const faultMat = new THREE.MeshBasicMaterial({
            color: 0xf59e0b, // Amber Warning indicator
            wireframe: true,
            transparent: true,
            opacity: 0.65
        });
        this.shearFaultMesh = new THREE.Mesh(faultGeom, faultMat);
        this.shearFaultMesh.position.set(4.5, 4.2, 1.8);
        this.shearFaultMesh.rotation.set(-0.9, 0.35, 0.25);
        this.terrainGroup.add(this.shearFaultMesh);
        // Hotspot Beacon Pin on the slip plane
        const pinGeom = new THREE.SphereGeometry(0.2, 16, 16);
        const pinMat = new THREE.MeshBasicMaterial({ color: 0xfacc15 });
        const pin = new THREE.Mesh(pinGeom, pinMat);
        pin.position.set(4.5, 4.8, 2.2);
        this.terrainGroup.add(pin);
    }
    /**
     * Atmospheric Alpine Mist & Cloud Particles
     */
    createAtmosphericMistParticles() {
        const count = 350;
        const geom = new THREE.BufferGeometry();
        const positions = new Float32Array(count * 3);
        for (let i = 0; i < count; i++) {
            const i3 = i * 3;
            positions[i3] = (Math.random() - 0.5) * 55;
            positions[i3 + 1] = Math.random() * 8.0 + 0.5; // Hovering above valleys
            positions[i3 + 2] = (Math.random() - 0.5) * 55;
        }
        geom.setAttribute("position", new THREE.BufferAttribute(positions, 3));
        const mat = new THREE.PointsMaterial({
            color: 0xd1fae5,
            size: 0.85,
            transparent: true,
            opacity: 0.28,
            blending: THREE.AdditiveBlending,
            fog: true
        });
        this.mistParticles = new THREE.Points(geom, mat);
        this.scene.add(this.mistParticles);
    }
    /**
     * GSAP ScrollTrigger Integration
     * Camera choreographs seamlessly through the 4 chapters with butter-smooth inertia.
     */
    setupGsapScrollScrubbing() {
        if (typeof gsap === "undefined" || typeof ScrollTrigger === "undefined") {
            console.warn("GSAP ScrollTrigger unavailable, relying on scroll listener fallback.");
            return;
        }
        gsap.registerPlugin(ScrollTrigger);
        const tl = gsap.timeline({
            scrollTrigger: {
                trigger: ".alpine-scroll-wrapper",
                start: "top top",
                end: "bottom bottom",
                scrub: 1.2, // Smooth inertia scrubbing
                onUpdate: (self) => {
                    this.onScrollProgress(self.progress);
                }
            }
        });
        // Chapter 0 -> Chapter 1: Swoop down from high ridge to steep shear plane
        tl.to(this.camera.position, {
            x: this.chapters[1].camPos.x,
            y: this.chapters[1].camPos.y,
            z: this.chapters[1].camPos.z,
            ease: "power2.inOut"
        }, 0.0);
        tl.to(this.terrainGroup.rotation, { y: 0.45, ease: "power2.inOut" }, 0.0);
        // Chapter 1 -> Chapter 2: Pivot around the mountain to saturated colluvium flank
        tl.to(this.camera.position, {
            x: this.chapters[2].camPos.x,
            y: this.chapters[2].camPos.y,
            z: this.chapters[2].camPos.z,
            ease: "power2.inOut"
        }, 0.33);
        tl.to(this.terrainGroup.rotation, { y: -0.35, ease: "power2.inOut" }, 0.33);
        // Chapter 2 -> Chapter 3: Descend directly toward valley floor highway corridor
        tl.to(this.camera.position, {
            x: this.chapters[3].camPos.x,
            y: this.chapters[3].camPos.y,
            z: this.chapters[3].camPos.z,
            ease: "power2.inOut"
        }, 0.66);
        tl.to(this.terrainGroup.rotation, { y: 0.15, ease: "power2.inOut" }, 0.66);
    }
    onScrollProgress(progress) {
        const total = this.chapters.length;
        const activeIdx = Math.min(total - 1, Math.floor(progress * total));
        if (activeIdx !== this.currentChapter) {
            this.currentChapter = activeIdx;
            this.updateTelemetryHUD(this.currentChapter);
        }
        // Update Top Navigation Bar Progress Lines
        const navItems = document.querySelectorAll(".alpine-nav-item");
        navItems.forEach((item, idx) => {
            const fill = item.querySelector(".nav-progress-fill");
            if (idx < this.currentChapter) {
                item.classList.add("completed");
                item.classList.remove("active");
                if (fill)
                    fill.style.width = "100%";
            }
            else if (idx === this.currentChapter) {
                item.classList.add("active");
                item.classList.remove("completed");
                const stepFraction = 1 / total;
                const progressInside = (progress - idx * stepFraction) / stepFraction;
                if (fill)
                    fill.style.width = `${Math.round(Math.max(0, Math.min(1, progressInside)) * 100)}%`;
            }
            else {
                item.classList.remove("active", "completed");
                if (fill)
                    fill.style.width = "0%";
            }
        });
    }
    updateTelemetryHUD(chapterIdx) {
        const chapter = this.chapters[chapterIdx];
        if (!chapter)
            return;
        const elElev = document.getElementById("hud-elev");
        const elSlope = document.getElementById("hud-slope");
        const elStatus = document.getElementById("hud-status");
        const elFeature = document.getElementById("hud-feature");
        if (elElev)
            elElev.textContent = chapter.elevation;
        if (elSlope)
            elSlope.textContent = chapter.slopeAngle;
        if (elStatus)
            elStatus.textContent = chapter.status;
        if (elFeature)
            elFeature.textContent = chapter.activeFeature;
    }
    bindEvents() {
        window.addEventListener("resize", () => {
            if (!this.camera || !this.renderer)
                return;
            const w = window.innerWidth;
            const h = window.innerHeight;
            this.camera.aspect = w / h;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(w, h);
            if (this.composer)
                this.composer.setSize(w, h);
        });
        // Mouse Parallax & Gentle Drag
        window.addEventListener("mousemove", (e) => {
            this.targetMouseX = (e.clientX / window.innerWidth) * 2 - 1;
            this.targetMouseY = -(e.clientY / window.innerHeight) * 2 + 1;
            if (this.isUserOrbiting) {
                const dx = e.clientX - this.dragStartX;
                const dy = e.clientY - this.dragStartY;
                this.orbitAngleY += dx * 0.003;
                this.orbitAngleX += dy * 0.003;
                this.dragStartX = e.clientX;
                this.dragStartY = e.clientY;
            }
        });
        window.addEventListener("mousedown", (e) => {
            const target = e.target;
            if (target && (target.tagName === "A" || target.tagName === "BUTTON" || target.closest(".alpine-nav-bar"))) {
                return;
            }
            this.isUserOrbiting = true;
            this.dragStartX = e.clientX;
            this.dragStartY = e.clientY;
        });
        window.addEventListener("mouseup", () => {
            this.isUserOrbiting = false;
        });
        // Click nav item smoothly scrolls
        document.querySelectorAll(".alpine-nav-item").forEach((item, idx) => {
            item.addEventListener("click", () => {
                const targetFrame = document.querySelector(`.alpine-frame[data-step="${idx}"]`);
                if (targetFrame) {
                    targetFrame.scrollIntoView({ behavior: "smooth" });
                }
            });
        });
    }
    animate() {
        requestAnimationFrame(() => this.animate());
        const dt = this.clock.getDelta();
        const t = this.clock.getElapsedTime();
        // Smooth Mouse Parallax
        this.mouseX += (this.targetMouseX - this.mouseX) * 0.05;
        this.mouseY += (this.targetMouseY - this.mouseY) * 0.05;
        // Apply mouse tilt to camera
        this.camera.position.x += this.mouseX * 0.02;
        this.camera.position.y += this.mouseY * 0.015;
        // User Orbit Offset Damping
        if (this.terrainGroup) {
            if (this.orbitAngleY !== 0) {
                this.terrainGroup.rotation.y += this.orbitAngleY * 0.1;
                this.orbitAngleY *= 0.88;
            }
            if (this.orbitAngleX !== 0) {
                this.terrainGroup.rotation.x += this.orbitAngleX * 0.1;
                this.orbitAngleX *= 0.88;
            }
        }
        // Animate LiDAR Topographic Contour Shader Uniforms
        if (this.terrainMaterial && this.terrainMaterial.uniforms) {
            this.terrainMaterial.uniforms.uTime.value = t;
        }
        // Pulsing Landslide Shear Fault Warning Plane
        if (this.shearFaultMesh) {
            this.shearFaultMesh.material.opacity = 0.45 + Math.sin(t * 3.5) * 0.25;
        }
        // Drifting Alpine Mist Particles
        if (this.mistParticles) {
            const pos = this.mistParticles.geometry.attributes.position.array;
            for (let i = 0; i < pos.length; i += 3) {
                pos[i] += 0.015; // Drift across valley
                if (pos[i] > 28)
                    pos[i] = -28;
            }
            this.mistParticles.geometry.attributes.position.needsUpdate = true;
        }
        // Render through Composer (UnrealBloom) or standard renderer
        if (this.composer) {
            this.composer.render();
        }
        else {
            this.renderer.render(this.scene, this.camera);
        }
    }
}
// Bootstrap on DOM ready
document.addEventListener("DOMContentLoaded", () => {
    new HimalayanTerrainShowcase();
});
