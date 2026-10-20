"use strict";
/**
 * ============================================================================
 * HIMA-LENS: 3D Himalayan Alpine Terrain & Kinematics Showcase
 * Awwwards "Site of the Day" Quality Architecture
 *
 * Uses Real 3D Production Mountain GLB Asset with PBR Materials & Textures
 * Combined with Three.js UnrealBloomPass, Volumetric Mist, & GSAP ScrollTrigger
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
        // Real 3D GLTF Mountain Model
        this.mountainModel = null;
        this.terrainGroup = null;
        this.shearFaultMesh = null;
        this.laserScanRing = null;
        this.mistParticles = null;
        this.highwayRibbon = null;
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
                camPos: { x: 0, y: 14, z: 24 },
                targetPos: { x: 0, y: 2, z: 0 },
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
                camPos: { x: -8.5, y: 6.8, z: 12 },
                targetPos: { x: 1.0, y: 2.5, z: 1.0 },
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
                camPos: { x: 8.5, y: 5.5, z: 11 },
                targetPos: { x: -1.5, y: 2.0, z: -0.5 },
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
                camPos: { x: 0.2, y: 3.2, z: 8.5 },
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
        this.loadReal3DMountainModel();
        this.createActiveShearPlane();
        this.createLaserScanRing();
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
        // Deep alpine twilight background
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
        this.renderer.toneMappingExposure = 1.35;
    }
    setupPostProcessing() {
        const w = window.innerWidth;
        const h = window.innerHeight;
        if (THREE.EffectComposer && THREE.RenderPass && THREE.UnrealBloomPass) {
            this.composer = new THREE.EffectComposer(this.renderer);
            const renderPass = new THREE.RenderPass(this.scene, this.camera);
            this.composer.addPass(renderPass);
            // Refined Optical Bloom for glowing radar scans and summit highlights
            const bloom = new THREE.UnrealBloomPass(new THREE.Vector2(w, h), 0.8, // Strength
            0.45, // Radius
            0.7 // Threshold
            );
            this.composer.addPass(bloom);
        }
    }
    setupAtmosphericLighting() {
        // Ambient sky fill (cool alpine teal-slate)
        const ambient = new THREE.AmbientLight(0x0d2822, 1.8);
        this.scene.add(ambient);
        // Golden Hour Sun over mountain peaks (dramatic shadows across valleys)
        const sun = new THREE.DirectionalLight(0xffeedd, 3.4);
        sun.position.set(28, 24, -18);
        sun.castShadow = true;
        this.scene.add(sun);
        // Soft cyan valley bounce light
        const bounce = new THREE.DirectionalLight(0x2dd4bf, 1.1);
        bounce.position.set(-22, -8, 16);
        this.scene.add(bounce);
    }
    /**
     * Load Genuine Production 3D Mountain Model (mountain.glb)
     * Features real photogrammetric mountain topology, high-resolution rock textures, and PBR shading.
     */
    loadReal3DMountainModel() {
        this.terrainGroup = new THREE.Group();
        this.scene.add(this.terrainGroup);
        if (!THREE.GLTFLoader) {
            console.error("GLTFLoader not loaded");
            return;
        }
        const loader = new THREE.GLTFLoader();
        loader.load("/static/models/mountain.glb", (gltf) => {
            this.mountainModel = gltf.scene;
            // Compute bounding box and normalize scale to 32 units across
            const box = new THREE.Box3().setFromObject(this.mountainModel);
            const size = box.getSize(new THREE.Vector3());
            const center = box.getCenter(new THREE.Vector3());
            const maxDim = Math.max(size.x, size.z);
            const scale = 32.0 / maxDim;
            this.mountainModel.scale.set(scale, scale, scale);
            this.mountainModel.position.set(-center.x * scale, -box.min.y * scale - 1.2, -center.z * scale);
            // Enhance materials with realistic alpine PBR values
            this.mountainModel.traverse((node) => {
                if (node.isMesh && node.material) {
                    node.material.roughness = Math.max(0.75, node.material.roughness || 0.8);
                    node.material.metalness = Math.min(0.25, node.material.metalness || 0.1);
                    node.receiveShadow = true;
                    node.castShadow = true;
                }
            });
            this.terrainGroup.add(this.mountainModel);
        }, undefined, (err) => {
            console.error("Error loading mountain.glb:", err);
        });
    }
    /**
     * Active Daylighting Landslide Shear Failure Plane
     * Displays a luminous planar rupture surface on a critical mountain cut-slope.
     */
    createActiveShearPlane() {
        const faultGeom = new THREE.PlaneGeometry(6.5, 4.2, 8, 8);
        const faultMat = new THREE.MeshBasicMaterial({
            color: 0xf59e0b, // Amber Warning indicator
            wireframe: true,
            transparent: true,
            opacity: 0.65
        });
        this.shearFaultMesh = new THREE.Mesh(faultGeom, faultMat);
        this.shearFaultMesh.position.set(3.2, 3.8, 2.2);
        this.shearFaultMesh.rotation.set(-0.85, 0.35, 0.2);
        this.terrainGroup.add(this.shearFaultMesh);
        // Warning Beacon Pin
        const pinGeom = new THREE.SphereGeometry(0.18, 16, 16);
        const pinMat = new THREE.MeshBasicMaterial({ color: 0xfacc15 });
        const pin = new THREE.Mesh(pinGeom, pinMat);
        pin.position.set(3.2, 4.2, 2.5);
        this.terrainGroup.add(pin);
    }
    /**
     * Dynamic InSAR & LiDAR Topographic Laser Scanner Ring
     * Sweeps smoothly across the mountain slopes, visualizing real-time elevation scanning.
     */
    createLaserScanRing() {
        const ringGeom = new THREE.RingGeometry(1.2, 1.4, 64);
        const ringMat = new THREE.MeshBasicMaterial({
            color: 0x2dd4bf,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.75
        });
        this.laserScanRing = new THREE.Mesh(ringGeom, ringMat);
        this.laserScanRing.rotation.x = -Math.PI / 2;
        this.laserScanRing.position.set(0, 2.0, 0);
        this.terrainGroup.add(this.laserScanRing);
    }
    /**
     * Atmospheric Alpine Mist & Cloud Particles
     */
    createAtmosphericMistParticles() {
        const count = 280;
        const geom = new THREE.BufferGeometry();
        const positions = new Float32Array(count * 3);
        for (let i = 0; i < count; i++) {
            const i3 = i * 3;
            positions[i3] = (Math.random() - 0.5) * 45;
            positions[i3 + 1] = Math.random() * 6.0 + 0.5;
            positions[i3 + 2] = (Math.random() - 0.5) * 45;
        }
        geom.setAttribute("position", new THREE.BufferAttribute(positions, 3));
        const mat = new THREE.PointsMaterial({
            color: 0xd1fae5,
            size: 0.9,
            transparent: true,
            opacity: 0.26,
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
        if (elElev)
            elElev.textContent = chapter.elevation;
        if (elSlope)
            elSlope.textContent = chapter.slopeAngle;
        if (elStatus)
            elStatus.textContent = chapter.status;
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
        this.camera.position.x += this.mouseX * 0.015;
        this.camera.position.y += this.mouseY * 0.012;
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
        // Animate LiDAR Laser Scanner Ring expanding across mountain
        if (this.laserScanRing) {
            const pulse = (t * 1.5) % 8.0;
            const rScale = pulse * 1.8 + 0.5;
            this.laserScanRing.scale.set(rScale, rScale, rScale);
            this.laserScanRing.position.y = 1.0 + Math.sin(t * 0.8) * 1.5;
            this.laserScanRing.material.opacity = Math.max(0.0, 0.8 - (pulse / 8.0));
        }
        // Pulsing Landslide Shear Fault Warning Plane
        if (this.shearFaultMesh) {
            this.shearFaultMesh.material.opacity = 0.45 + Math.sin(t * 3.5) * 0.25;
        }
        // Drifting Alpine Mist Particles
        if (this.mistParticles) {
            const pos = this.mistParticles.geometry.attributes.position.array;
            for (let i = 0; i < pos.length; i += 3) {
                pos[i] += 0.012;
                if (pos[i] > 22)
                    pos[i] = -22;
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
// Bootstrap
document.addEventListener("DOMContentLoaded", () => {
    new HimalayanTerrainShowcase();
});
