"use strict";
/**
 * ============================================================================
 * HIMA-LENS: Satellite Intelligence & Earth Observation Service
 * Inspired by EnduroSat Space Service (Awwwards-Winning WebGL Digital Experience)
 * Written in TypeScript (ES2020) with Three.js WebGL Engine
 * ============================================================================
 */
class SatelliteServiceApp {
    constructor() {
        this.canvas = null;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.starfield = null;
        this.earthGroup = null;
        this.earthMesh = null;
        this.cloudMesh = null;
        this.himachalMarker = null;
        this.satelliteGroup = null;
        this.solarPanels = [];
        this.radarCone = null;
        this.telemetryRays = null;
        this.orbitLine = null;
        this.scrollProgress = 0;
        this.targetScrollProgress = 0;
        this.currentStep = 0;
        this.mouseX = 0;
        this.mouseY = 0;
        this.targetMouseX = 0;
        this.targetMouseY = 0;
        this.isUserDragging = false;
        this.dragStartMouseX = 0;
        this.dragStartMouseY = 0;
        this.dragOffsetRotX = 0;
        this.dragOffsetRotY = 0;
        this.isRunning = true;
        this.clock = null;
        this.steps = [
            // Step 0: Hero / LEO Overview
            {
                camX: 0,
                camY: 3.2,
                camZ: 14.5,
                targetX: 0,
                targetY: 0,
                targetZ: 0,
                satDistance: 8.2,
                satAngle: 0.35,
                beamIntensity: 0.4,
                earthRotationSpeed: 0.0012
            },
            // Step 1: Synthetic Aperture Radar (SAR Antenna & Avionics focus)
            {
                camX: -4.8,
                camY: 2.1,
                camZ: 9.8,
                targetX: 2.2,
                targetY: 1.5,
                targetZ: 0,
                satDistance: 7.5,
                satAngle: 0.95,
                beamIntensity: 0.85,
                earthRotationSpeed: 0.0008
            },
            // Step 2: Atmospheric Trigger & Inundation Radar
            {
                camX: 3.5,
                camY: 5.2,
                camZ: 8.5,
                targetX: 0.5,
                targetY: 0.8,
                targetZ: 0,
                satDistance: 7.8,
                satAngle: 1.75,
                beamIntensity: 1.0,
                earthRotationSpeed: 0.0005
            },
            // Step 3: Kinematic Inference & Sub-mm Ground Displacement
            {
                camX: -2.0,
                camY: 6.8,
                camZ: 7.5,
                targetX: 0,
                targetY: 1.2,
                targetZ: 0,
                satDistance: 7.2,
                satAngle: 2.45,
                beamIntensity: 0.9,
                earthRotationSpeed: 0.0006
            },
            // Step 4: Autonomous Operations Hub & Corridor Telemetry
            {
                camX: 5.2,
                camY: 3.5,
                camZ: 10.5,
                targetX: -1.0,
                targetY: 0.5,
                targetZ: 0,
                satDistance: 8.0,
                satAngle: 3.14,
                beamIntensity: 0.6,
                earthRotationSpeed: 0.001
            }
        ];
        this.init();
    }
    init() {
        this.canvas = document.getElementById("space-webgl-canvas");
        if (!this.canvas || typeof THREE === "undefined") {
            console.error("Three.js or space-webgl-canvas not available");
            return;
        }
        this.clock = new THREE.Clock();
        this.setupScene();
        this.createStarfield();
        this.createEarthAndHimalaya();
        this.createSatelliteModel();
        this.createRadarBeamAndOrbit();
        this.bindEvents();
        this.updateNavigationUI(0);
        this.animate();
    }
    setupScene() {
        const w = window.innerWidth;
        const h = window.innerHeight;
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x020705);
        this.scene.fog = new THREE.FogExp2(0x020705, 0.025);
        this.camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 1000);
        this.camera.position.set(this.steps[0].camX, this.steps[0].camY, this.steps[0].camZ);
        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            antialias: true,
            alpha: true,
            powerPreference: "high-performance"
        });
        this.renderer.setSize(w, h);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.15;
        // Space Lighting
        const ambientLight = new THREE.AmbientLight(0x0d2822, 1.2);
        this.scene.add(ambientLight);
        // Sunlight (directional from deep space)
        const sunLight = new THREE.DirectionalLight(0xffffff, 2.4);
        sunLight.position.set(15, 8, 12);
        this.scene.add(sunLight);
        // Subtle cyan rim backlight
        const rimLight = new THREE.DirectionalLight(0x2dd4bf, 1.1);
        rimLight.position.set(-12, -6, -8);
        this.scene.add(rimLight);
    }
    createStarfield() {
        const starCount = 1800;
        const starGeometry = new THREE.BufferGeometry();
        const positions = new Float32Array(starCount * 3);
        const colors = new Float32Array(starCount * 3);
        const colorTeal = new THREE.Color(0x2dd4bf);
        const colorWhite = new THREE.Color(0xffffff);
        const colorAmber = new THREE.Color(0xfacc15);
        for (let i = 0; i < starCount; i++) {
            const i3 = i * 3;
            const radius = 60 + Math.random() * 80;
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos((Math.random() * 2) - 1);
            positions[i3] = radius * Math.sin(phi) * Math.cos(theta);
            positions[i3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
            positions[i3 + 2] = radius * Math.cos(phi);
            const rnd = Math.random();
            let c = colorWhite;
            if (rnd > 0.8)
                c = colorTeal;
            else if (rnd > 0.65)
                c = colorAmber;
            colors[i3] = c.r;
            colors[i3 + 1] = c.g;
            colors[i3 + 2] = c.b;
        }
        starGeometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
        starGeometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
        const starMaterial = new THREE.PointsMaterial({
            size: 0.9,
            vertexColors: true,
            transparent: true,
            opacity: 0.85,
            fog: false
        });
        this.starfield = new THREE.Points(starGeometry, starMaterial);
        this.scene.add(this.starfield);
    }
    /**
     * Procedural Earth texture with continental masses & highlighted Himalayan ridge
     */
    createProceduralEarthTexture() {
        const canvas = document.createElement("canvas");
        canvas.width = 1024;
        canvas.height = 512;
        const ctx = canvas.getContext("2d");
        // Base ocean gradient
        const oceanGrad = ctx.createLinearGradient(0, 0, 0, 512);
        oceanGrad.addColorStop(0, "#011311");
        oceanGrad.addColorStop(0.5, "#032822");
        oceanGrad.addColorStop(1, "#011311");
        ctx.fillStyle = oceanGrad;
        ctx.fillRect(0, 0, 1024, 512);
        // Continental landmasses (stylized geospatial continents)
        ctx.fillStyle = "#0c3b2e";
        // Eurasia & Indian subcontinent
        ctx.beginPath();
        ctx.ellipse(650, 180, 160, 90, 0, 0, Math.PI * 2);
        ctx.fill();
        // Indian peninsula
        ctx.beginPath();
        ctx.moveTo(630, 210);
        ctx.lineTo(690, 210);
        ctx.lineTo(660, 280);
        ctx.closePath();
        ctx.fillStyle = "#104c3b";
        ctx.fill();
        // Himalayan Alpine Arc (high relief highlighted)
        ctx.strokeStyle = "#2dd4bf";
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.arc(660, 195, 30, Math.PI * 0.85, Math.PI * 1.8);
        ctx.stroke();
        // Africa
        ctx.fillStyle = "#082d23";
        ctx.beginPath();
        ctx.ellipse(510, 250, 80, 110, 0.2, 0, Math.PI * 2);
        ctx.fill();
        // Americas
        ctx.beginPath();
        ctx.ellipse(260, 180, 70, 90, -0.2, 0, Math.PI * 2);
        ctx.ellipse(320, 310, 60, 100, 0.3, 0, Math.PI * 2);
        ctx.fill();
        // Latitude & Longitude Geodetic Grid
        ctx.strokeStyle = "rgba(45, 212, 191, 0.08)";
        ctx.lineWidth = 1;
        for (let x = 0; x < 1024; x += 64) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, 512);
            ctx.stroke();
        }
        for (let y = 0; y < 512; y += 42) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(1024, y);
            ctx.stroke();
        }
        // Concentric radar beacon at Himachal Pradesh coordinates
        const hpX = 660;
        const hpY = 195;
        ctx.strokeStyle = "#5eead4";
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        ctx.arc(hpX, hpY, 6, 0, Math.PI * 2);
        ctx.stroke();
        ctx.fillStyle = "#facc15";
        ctx.beginPath();
        ctx.arc(hpX, hpY, 3, 0, Math.PI * 2);
        ctx.fill();
        const texture = new THREE.CanvasTexture(canvas);
        texture.wrapS = THREE.RepeatWrapping;
        texture.wrapT = THREE.ClampToEdgeWrapping;
        return texture;
    }
    createEarthAndHimalaya() {
        this.earthGroup = new THREE.Group();
        this.earthGroup.position.set(0, -1.8, 0);
        const earthRadius = 4.2;
        const earthGeom = new THREE.SphereGeometry(earthRadius, 64, 48);
        const earthTex = this.createProceduralEarthTexture();
        const earthMat = new THREE.MeshStandardMaterial({
            map: earthTex,
            roughness: 0.65,
            metalness: 0.25,
            emissive: 0x031812,
            emissiveIntensity: 0.3
        });
        this.earthMesh = new THREE.Mesh(earthGeom, earthMat);
        this.earthGroup.add(this.earthMesh);
        // Atmosphere Fresnel Glow Layer
        const atmosGeom = new THREE.SphereGeometry(earthRadius * 1.035, 48, 36);
        const atmosMat = new THREE.MeshStandardMaterial({
            color: 0x2dd4bf,
            transparent: true,
            opacity: 0.18,
            blending: THREE.AdditiveBlending,
            side: THREE.BackSide,
            wireframe: false
        });
        const atmosphere = new THREE.Mesh(atmosGeom, atmosMat);
        this.earthGroup.add(atmosphere);
        // Swirling Semi-Transparent Cloud / Weather Layer
        const cloudGeom = new THREE.SphereGeometry(earthRadius * 1.015, 48, 36);
        const cloudMat = new THREE.MeshLambertMaterial({
            color: 0xffffff,
            transparent: true,
            opacity: 0.16,
            blending: THREE.NormalBlending
        });
        this.cloudMesh = new THREE.Mesh(cloudGeom, cloudMat);
        this.earthGroup.add(this.cloudMesh);
        // Pulsing Himachal Target Marker (Pin & Beacon Ring)
        const markerGroup = new THREE.Group();
        // Himachal position on the sphere surface (lat ~31.5, lon ~77)
        const phi = (90 - 31.5) * (Math.PI / 180);
        const theta = (77.2 + 180) * (Math.PI / 180);
        const mx = -(earthRadius * 1.01 * Math.sin(phi) * Math.cos(theta));
        const my = earthRadius * 1.01 * Math.cos(phi);
        const mz = earthRadius * 1.01 * Math.sin(phi) * Math.sin(theta);
        markerGroup.position.set(mx, my, mz);
        const pinGeom = new THREE.CylinderGeometry(0.04, 0.01, 0.45, 12);
        pinGeom.translate(0, 0.22, 0);
        const pinMat = new THREE.MeshBasicMaterial({ color: 0x2dd4bf });
        const pinMesh = new THREE.Mesh(pinGeom, pinMat);
        pinMesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), markerGroup.position.clone().normalize());
        markerGroup.add(pinMesh);
        const ringGeom = new THREE.RingGeometry(0.12, 0.18, 24);
        const ringMat = new THREE.MeshBasicMaterial({
            color: 0x5eead4,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.9
        });
        const ringMesh = new THREE.Mesh(ringGeom, ringMat);
        ringMesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), markerGroup.position.clone().normalize());
        markerGroup.add(ringMesh);
        this.himachalMarker = markerGroup;
        this.earthGroup.add(this.himachalMarker);
        this.scene.add(this.earthGroup);
    }
    /**
     * Procedural High-Fidelity Earth Observation Satellite
     * Features: Gold MLI avionics bus, twin solar arrays, C-band SAR phased array antenna,
     * sub-reflector, star trackers, and blinking avionics LEDs.
     */
    createSatelliteModel() {
        this.satelliteGroup = new THREE.Group();
        // 1. Central Avionics Bus (Gold Multi-Layer Insulation Foil)
        const busGeom = new THREE.BoxGeometry(1.2, 0.9, 1.8);
        const busMat = new THREE.MeshStandardMaterial({
            color: 0xd4af37, // Gold MLI
            metalness: 0.85,
            roughness: 0.35,
            bumpScale: 0.05
        });
        const busMesh = new THREE.Mesh(busGeom, busMat);
        this.satelliteGroup.add(busMesh);
        // Top Equipment Deck (Titanium dark finish)
        const deckGeom = new THREE.BoxGeometry(1.24, 0.1, 1.84);
        const deckMat = new THREE.MeshStandardMaterial({
            color: 0x1e293b,
            metalness: 0.9,
            roughness: 0.2
        });
        const deckMesh = new THREE.Mesh(deckGeom, deckMat);
        deckMesh.position.y = 0.5;
        this.satelliteGroup.add(deckMesh);
        // 2. Synthetic Aperture Radar (SAR) Phased-Array Antenna
        const sarGeom = new THREE.BoxGeometry(0.8, 0.08, 3.2);
        const sarMat = new THREE.MeshStandardMaterial({
            color: 0xffffff,
            metalness: 0.6,
            roughness: 0.4
        });
        const sarMesh = new THREE.Mesh(sarGeom, sarMat);
        sarMesh.position.set(0, -0.65, 0);
        this.satelliteGroup.add(sarMesh);
        // Antenna Grid Lines on SAR
        const sarGridGeom = new THREE.PlaneGeometry(0.76, 3.1);
        const sarGridMat = new THREE.MeshBasicMaterial({
            color: 0x2dd4bf,
            wireframe: true,
            transparent: true,
            opacity: 0.45
        });
        const sarGridMesh = new THREE.Mesh(sarGridGeom, sarGridMat);
        sarGridMesh.rotation.x = Math.PI / 2;
        sarGridMesh.position.set(0, -0.7, 0);
        this.satelliteGroup.add(sarGridMesh);
        // 3. Parabolic High-Gain Telemetry Dish
        const dishGeom = new THREE.SphereGeometry(0.45, 24, 16, 0, Math.PI * 2, 0, Math.PI * 0.45);
        const dishMat = new THREE.MeshStandardMaterial({
            color: 0xe2e8f0,
            metalness: 0.7,
            roughness: 0.3,
            side: THREE.DoubleSide
        });
        const dishMesh = new THREE.Mesh(dishGeom, dishMat);
        dishMesh.rotation.x = -Math.PI / 2;
        dishMesh.position.set(0, 0.75, 0.55);
        this.satelliteGroup.add(dishMesh);
        // Dish Feed Horn / Boom
        const hornGeom = new THREE.CylinderGeometry(0.02, 0.04, 0.35, 12);
        const hornMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.9, roughness: 0.1 });
        const hornMesh = new THREE.Mesh(hornGeom, hornMat);
        hornMesh.position.set(0, 0.95, 0.55);
        this.satelliteGroup.add(hornMesh);
        // 4. Twin Deployable Photovoltaic Solar Arrays
        const panelWidth = 3.6;
        const panelHeight = 0.04;
        const panelDepth = 1.1;
        const panelMat = new THREE.MeshStandardMaterial({
            color: 0x0f3460, // Deep silicon blue
            metalness: 0.9,
            roughness: 0.15,
            emissive: 0x071e3d,
            emissiveIntensity: 0.25
        });
        // Left Solar Wing
        const leftWingGroup = new THREE.Group();
        const leftWing = new THREE.Mesh(new THREE.BoxGeometry(panelWidth, panelHeight, panelDepth), panelMat);
        leftWing.position.x = -(panelWidth / 2 + 0.9);
        leftWingGroup.add(leftWing);
        // Left Wing Mount Boom
        const boomLeft = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.9, 12), new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.9 }));
        boomLeft.rotation.z = Math.PI / 2;
        boomLeft.position.x = -0.55;
        leftWingGroup.add(boomLeft);
        this.satelliteGroup.add(leftWingGroup);
        this.solarPanels.push(leftWingGroup);
        // Right Solar Wing
        const rightWingGroup = new THREE.Group();
        const rightWing = new THREE.Mesh(new THREE.BoxGeometry(panelWidth, panelHeight, panelDepth), panelMat);
        rightWing.position.x = (panelWidth / 2 + 0.9);
        rightWingGroup.add(rightWing);
        // Right Wing Mount Boom
        const boomRight = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.9, 12), new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.9 }));
        boomRight.rotation.z = Math.PI / 2;
        boomRight.position.x = 0.55;
        rightWingGroup.add(boomRight);
        this.satelliteGroup.add(rightWingGroup);
        this.solarPanels.push(rightWingGroup);
        // 5. Star Trackers & Optical Lenses
        const trackerGeom = new THREE.CylinderGeometry(0.08, 0.08, 0.25, 16);
        const trackerMat = new THREE.MeshStandardMaterial({ color: 0x050c0a, roughness: 0.1 });
        const tracker1 = new THREE.Mesh(trackerGeom, trackerMat);
        tracker1.position.set(0.4, 0.55, -0.6);
        this.satelliteGroup.add(tracker1);
        // 6. Navigation Strobe LEDs (Green / Cyan)
        const ledGeom = new THREE.SphereGeometry(0.06, 12, 12);
        const ledMat = new THREE.MeshBasicMaterial({ color: 0x2dd4bf });
        const led1 = new THREE.Mesh(ledGeom, ledMat);
        led1.position.set(-panelWidth - 0.9, 0.05, 0);
        this.satelliteGroup.add(led1);
        const led2 = new THREE.Mesh(ledGeom, ledMat);
        led2.position.set(panelWidth + 0.9, 0.05, 0);
        this.satelliteGroup.add(led2);
        // Initial scale and position in orbit
        this.satelliteGroup.scale.set(0.55, 0.55, 0.55);
        this.satelliteGroup.position.set(4.5, 4.2, 3.5);
        this.satelliteGroup.rotation.y = -0.5;
        this.satelliteGroup.rotation.z = 0.2;
        this.scene.add(this.satelliteGroup);
    }
    /**
     * InSAR Radar Scanning Cone & Downlink Telemetry Stream
     */
    createRadarBeamAndOrbit() {
        // Orbit Ellipse Path
        const orbitCurve = new THREE.EllipseCurve(0, 0, 6.8, 6.2, 0, 2 * Math.PI, false, 0);
        const points = orbitCurve.getPoints(120);
        const orbitGeom = new THREE.BufferGeometry().setFromPoints(points.map((p) => new THREE.Vector3(p.x, 0, p.y)));
        const orbitMat = new THREE.LineBasicMaterial({
            color: 0x2dd4bf,
            transparent: true,
            opacity: 0.22
        });
        this.orbitLine = new THREE.Line(orbitGeom, orbitMat);
        this.orbitLine.rotation.x = Math.PI / 4.2;
        this.orbitLine.rotation.y = Math.PI / 6;
        this.scene.add(this.orbitLine);
        // InSAR Volumetric Scanning Cone (Teal Translucent Beam)
        const coneGeom = new THREE.ConeGeometry(2.4, 6.5, 32, 1, true);
        coneGeom.translate(0, -3.25, 0);
        const coneMat = new THREE.MeshBasicMaterial({
            color: 0x2dd4bf,
            transparent: true,
            opacity: 0.18,
            side: THREE.DoubleSide,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        });
        this.radarCone = new THREE.Mesh(coneGeom, coneMat);
        this.satelliteGroup.add(this.radarCone);
        // Telemetry Data Stream Particles
        const particleCount = 120;
        const particleGeom = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);
        for (let i = 0; i < particleCount; i++) {
            const i3 = i * 3;
            positions[i3] = (Math.random() - 0.5) * 1.5;
            positions[i3 + 1] = -Math.random() * 6.5;
            positions[i3 + 2] = (Math.random() - 0.5) * 1.5;
        }
        particleGeom.setAttribute("position", new THREE.BufferAttribute(positions, 3));
        const particleMat = new THREE.PointsMaterial({
            color: 0x5eead4,
            size: 0.12,
            transparent: true,
            opacity: 0.75,
            blending: THREE.AdditiveBlending
        });
        this.telemetryRays = new THREE.Points(particleGeom, particleMat);
        this.satelliteGroup.add(this.telemetryRays);
    }
    bindEvents() {
        window.addEventListener("resize", () => this.onWindowResize());
        // Scroll listener driving narrative frames & camera poses
        window.addEventListener("scroll", () => {
            const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
            if (maxScroll > 0) {
                this.targetScrollProgress = window.scrollY / maxScroll;
            }
        }, { passive: true });
        // Mouse Parallax & Drag Orbit
        window.addEventListener("mousemove", (e) => {
            this.targetMouseX = (e.clientX / window.innerWidth) * 2 - 1;
            this.targetMouseY = -(e.clientY / window.innerHeight) * 2 + 1;
            if (this.isUserDragging) {
                const deltaX = e.clientX - this.dragStartMouseX;
                const deltaY = e.clientY - this.dragStartMouseY;
                this.dragOffsetRotY += deltaX * 0.005;
                this.dragOffsetRotX += deltaY * 0.005;
                this.dragStartMouseX = e.clientX;
                this.dragStartMouseY = e.clientY;
            }
        });
        window.addEventListener("mousedown", (e) => {
            // Only drag on canvas / background, not on buttons or links
            const target = e.target;
            if (target && (target.tagName === "BUTTON" || target.tagName === "A" || target.closest(".fps-navigation-bar"))) {
                return;
            }
            this.isUserDragging = true;
            this.dragStartMouseX = e.clientX;
            this.dragStartMouseY = e.clientY;
        });
        window.addEventListener("mouseup", () => {
            this.isUserDragging = false;
        });
        // Interactive Lifecycle Navigation Bar Clicks
        const navSections = document.querySelectorAll(".fps-nav-section");
        navSections.forEach((sec, idx) => {
            sec.addEventListener("click", () => {
                this.scrollToStep(idx);
            });
        });
        // Floating Presets
        const btnOrbit = document.getElementById("btn-toggle-orbit");
        if (btnOrbit) {
            btnOrbit.addEventListener("click", () => {
                btnOrbit.classList.toggle("active");
            });
        }
        const btnBeam = document.getElementById("btn-toggle-beam");
        if (btnBeam) {
            btnBeam.addEventListener("click", () => {
                const isActive = btnBeam.classList.toggle("active");
                if (this.radarCone)
                    this.radarCone.visible = isActive;
                if (this.telemetryRays)
                    this.telemetryRays.visible = isActive;
            });
        }
    }
    scrollToStep(stepIndex) {
        const frame = document.querySelector(`.fps-frame[data-step="${stepIndex}"]`);
        if (frame) {
            frame.scrollIntoView({ behavior: "smooth" });
        }
    }
    onWindowResize() {
        if (!this.camera || !this.renderer)
            return;
        const w = window.innerWidth;
        const h = window.innerHeight;
        this.camera.aspect = w / h;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(w, h);
    }
    updateNavigationUI(stepFraction) {
        const totalSteps = this.steps.length;
        const currentActiveStep = Math.min(totalSteps - 1, Math.floor(stepFraction * (totalSteps - 1) + 0.35));
        if (currentActiveStep !== this.currentStep) {
            this.currentStep = currentActiveStep;
        }
        const navSections = document.querySelectorAll(".fps-nav-section");
        navSections.forEach((sec, idx) => {
            const fill = sec.querySelector(".fps-progress-fill");
            if (idx < this.currentStep) {
                sec.classList.add("completed");
                sec.classList.remove("active");
                if (fill)
                    fill.style.width = "100%";
            }
            else if (idx === this.currentStep) {
                sec.classList.add("active");
                sec.classList.remove("completed");
                // Calculate partial fill inside current step
                const stepSpan = 1 / (totalSteps - 1);
                const stepStart = idx * stepSpan;
                const progressInside = Math.max(0, Math.min(1, (stepFraction - stepStart) / stepSpan));
                if (fill)
                    fill.style.width = `${Math.round(progressInside * 100)}%`;
            }
            else {
                sec.classList.remove("active", "completed");
                if (fill)
                    fill.style.width = "0%";
            }
        });
        // Sync live telemetry pill stats based on active step
        const telemAlt = document.getElementById("telem-altitude");
        const telemMode = document.getElementById("telem-mode");
        const telemRevisit = document.getElementById("telem-revisit");
        if (telemAlt && telemMode && telemRevisit) {
            switch (this.currentStep) {
                case 0:
                    telemAlt.textContent = "690 KM LEO";
                    telemMode.textContent = "ORBITAL INGESTION";
                    telemRevisit.textContent = "12-DAY CADENCE";
                    break;
                case 1:
                    telemAlt.textContent = "690 KM";
                    telemMode.textContent = "C-BAND SAR ACTIVE";
                    telemRevisit.textContent = "5.405 GHz SCAN";
                    break;
                case 2:
                    telemAlt.textContent = "DOPPLER 3.2 KM";
                    telemMode.textContent = "PRECIPITATION FLUX";
                    telemRevisit.textContent = "38.5 mm/hr TRIGGER";
                    break;
                case 3:
                    telemAlt.textContent = "1.5m DEM RES";
                    telemMode.textContent = "INTERFEROGRAM KINEMATICS";
                    telemRevisit.textContent = "0.5mm PRECISION";
                    break;
                case 4:
                default:
                    telemAlt.textContent = "SURFACE HUB";
                    telemMode.textContent = "DISASTER OPS ACTIVE";
                    telemRevisit.textContent = "REAL-TIME PUSH";
                    break;
            }
        }
    }
    animate() {
        if (!this.isRunning)
            return;
        requestAnimationFrame(() => this.animate());
        const delta = this.clock.getDelta();
        const elapsedTime = this.clock.getElapsedTime();
        // 1. Lerp scroll progress for ultra-smooth inertia transitions
        this.scrollProgress += (this.targetScrollProgress - this.scrollProgress) * 0.08;
        this.updateNavigationUI(this.scrollProgress);
        // 2. Interpolate Camera Pose between current and next step
        const totalSteps = this.steps.length;
        const scaledProgress = this.scrollProgress * (totalSteps - 1);
        const baseIndex = Math.min(totalSteps - 2, Math.floor(scaledProgress));
        const nextIndex = Math.min(totalSteps - 1, baseIndex + 1);
        const t = Math.max(0, Math.min(1, scaledProgress - baseIndex));
        const pA = this.steps[baseIndex];
        const pB = this.steps[nextIndex];
        // Smooth cubic ease for pose transitions
        const easeT = t * t * (3 - 2 * t);
        const targetCamX = pA.camX + (pB.camX - pA.camX) * easeT;
        const targetCamY = pA.camY + (pB.camY - pA.camY) * easeT;
        const targetCamZ = pA.camZ + (pB.camZ - pA.camZ) * easeT;
        const lookAtX = pA.targetX + (pB.targetX - pA.targetX) * easeT;
        const lookAtY = pA.targetY + (pB.targetY - pA.targetY) * easeT;
        const lookAtZ = pA.targetZ + (pB.targetZ - pA.targetZ) * easeT;
        // Mouse Parallax Lerp
        this.mouseX += (this.targetMouseX - this.mouseX) * 0.05;
        this.mouseY += (this.targetMouseY - this.mouseY) * 0.05;
        this.camera.position.x = targetCamX + this.mouseX * 0.45;
        this.camera.position.y = targetCamY + this.mouseY * 0.35;
        this.camera.position.z = targetCamZ;
        this.camera.lookAt(lookAtX, lookAtY, lookAtZ);
        // 3. Earth Rotation & Himachal Beacon Pulse
        const rotSpeed = pA.earthRotationSpeed + (pB.earthRotationSpeed - pA.earthRotationSpeed) * easeT;
        if (this.earthGroup) {
            this.earthGroup.rotation.y += rotSpeed + (this.isUserDragging ? 0 : 0.0003);
            if (this.dragOffsetRotY !== 0) {
                this.earthGroup.rotation.y += this.dragOffsetRotY * 0.1;
                this.dragOffsetRotY *= 0.9;
            }
            if (this.dragOffsetRotX !== 0) {
                this.earthGroup.rotation.x += this.dragOffsetRotX * 0.1;
                this.dragOffsetRotX *= 0.9;
            }
        }
        if (this.cloudMesh) {
            this.cloudMesh.rotation.y += rotSpeed * 1.35;
        }
        // 4. Satellite Orbit Animation & Solar Tracking
        if (this.satelliteGroup) {
            const orbitDist = pA.satDistance + (pB.satDistance - pA.satDistance) * easeT;
            const orbitAngle = (pA.satAngle + (pB.satAngle - pA.satAngle) * easeT) + (elapsedTime * 0.08);
            this.satelliteGroup.position.x = Math.cos(orbitAngle) * orbitDist;
            this.satelliteGroup.position.z = Math.sin(orbitAngle) * orbitDist;
            this.satelliteGroup.position.y = 2.8 + Math.sin(orbitAngle * 1.8) * 0.9;
            // Orient satellite toward Earth surface
            this.satelliteGroup.lookAt(0, -1.8, 0);
            // Subtle roll & pitch float
            this.satelliteGroup.rotation.z += Math.sin(elapsedTime * 1.5) * 0.04;
            // Animate solar panels slow sun-tracking angle
            this.solarPanels.forEach((wing, wIdx) => {
                wing.rotation.x = Math.sin(elapsedTime * 0.3 + wIdx) * 0.12;
            });
        }
        // 5. Radar Beam Pulses & Telemetry Rays
        if (this.radarCone) {
            const targetBeamOpacity = (pA.beamIntensity + (pB.beamIntensity - pA.beamIntensity) * easeT) * 0.22;
            this.radarCone.material.opacity = targetBeamOpacity * (0.8 + Math.sin(elapsedTime * 4.0) * 0.2);
        }
        if (this.telemetryRays) {
            const pos = this.telemetryRays.geometry.attributes.position.array;
            for (let i = 1; i < pos.length; i += 3) {
                pos[i] -= 0.12; // Stream down to earth
                if (pos[i] < -6.5) {
                    pos[i] = 0; // Reset to satellite antenna
                }
            }
            this.telemetryRays.geometry.attributes.position.needsUpdate = true;
        }
        // 6. Slowly rotate starfield for cosmic immersion
        if (this.starfield) {
            this.starfield.rotation.y = elapsedTime * 0.0008;
        }
        this.renderer.render(this.scene, this.camera);
    }
}
// Bootstrap on DOM ready
document.addEventListener("DOMContentLoaded", () => {
    new SatelliteServiceApp();
});
