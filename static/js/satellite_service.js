"use strict";
/**
 * ============================================================================
 * HIMA-LENS: Space-to-Slope Satellite & Terrain Intelligence Experience
 * Inspired by EnduroSat Space Service (Awwwards SOTD Polish)
 *
 * Features:
 *  - NASA High-Resolution PBR Earth (Atmos, Normal, Specular, Clouds)
 *  - Atmospheric Rayleigh/Mie Fresnel Glow GLSL Shader
 *  - Real 3D GLTF Satellite / Spacecraft Mesh
 *  - Hyper-Detailed 3D Himalayan Mountain Massif with Procedural Alpine Relief
 *  - Animated InSAR LiDAR Elevation Contour Scan Wavefronts
 *  - Daylighting Landslide Slip Plane & Creep Vector Visualizer
 *  - Three.js EffectComposer with UnrealBloomPass Optical Glare
 *  - GSAP & ScrollTrigger Scrubbed Cinematic Camera Choreography
 * ============================================================================
 */
class SatelliteServiceApp {
    constructor() {
        this.canvas = null;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.composer = null;
        this.clock = null;
        // 3D Objects
        this.spaceGroup = null;
        this.earthMesh = null;
        this.cloudMesh = null;
        this.atmosphereMesh = null;
        this.himachalBeacon = null;
        this.satelliteModel = null;
        this.insarBeamMesh = null;
        this.telemetryStream = null;
        // Mountain Terrain Objects
        this.terrainGroup = null;
        this.mountainMesh = null;
        this.contourScanMesh = null;
        this.landslideFaultMesh = null;
        this.highwayLineMesh = null;
        // State
        this.isBloomEnabled = true;
        this.currentPhaseIndex = 0;
        this.mouseX = 0;
        this.mouseY = 0;
        this.targetMouseX = 0;
        this.targetMouseY = 0;
        this.init();
    }
    init() {
        this.canvas = document.getElementById("space-webgl-canvas");
        if (!this.canvas || typeof THREE === "undefined") {
            console.error("Three.js or canvas not available");
            return;
        }
        this.clock = new THREE.Clock();
        this.setupRendererAndCamera();
        this.setupPostProcessing();
        this.createDeepSpaceCosmos();
        this.createPhotorealisticEarth();
        this.loadGltfSatellite();
        this.createInSARBeam();
        this.createHimalayanMassif();
        this.bindUserInteractions();
        this.setupGsapScrollTimeline();
        this.animate();
    }
    setupRendererAndCamera() {
        const w = window.innerWidth;
        const h = window.innerHeight;
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x010504);
        this.scene.fog = new THREE.FogExp2(0x010504, 0.015);
        this.camera = new THREE.PerspectiveCamera(42, w / h, 0.1, 1000);
        this.camera.position.set(0, 4, 16);
        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            antialias: true,
            alpha: true,
            powerPreference: "high-performance"
        });
        this.renderer.setSize(w, h);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.2;
        // Cinematic Lighting
        const ambientLight = new THREE.AmbientLight(0x0c251f, 1.4);
        this.scene.add(ambientLight);
        // Sun Directional Light
        const sun = new THREE.DirectionalLight(0xffffff, 2.6);
        sun.position.set(16, 8, 14);
        this.scene.add(sun);
        // Rim Light from dark space
        const rim = new THREE.DirectionalLight(0x2dd4bf, 1.2);
        rim.position.set(-14, -6, -10);
        this.scene.add(rim);
    }
    /**
     * Optical Post-Processing Pipeline (UnrealBloomPass)
     * Creates real optical luminescence on lasers, beacons, and atmospheric rim.
     */
    setupPostProcessing() {
        const w = window.innerWidth;
        const h = window.innerHeight;
        if (THREE.EffectComposer && THREE.RenderPass && THREE.UnrealBloomPass) {
            this.composer = new THREE.EffectComposer(this.renderer);
            const renderPass = new THREE.RenderPass(this.scene, this.camera);
            this.composer.addPass(renderPass);
            // High-Threshold Optical Bloom
            const bloomPass = new THREE.UnrealBloomPass(new THREE.Vector2(w, h), 0.95, // Strength (subtle, non-muddy)
            0.45, // Radius
            0.72 // Threshold (only bright highlights bloom)
            );
            this.composer.addPass(bloomPass);
            this.isBloomEnabled = true;
        }
        else {
            this.isBloomEnabled = false;
        }
    }
    /**
     * Cosmic Starfield & Nebula Dust
     */
    createDeepSpaceCosmos() {
        const count = 2200;
        const geom = new THREE.BufferGeometry();
        const positions = new Float32Array(count * 3);
        const colors = new Float32Array(count * 3);
        const cWhite = new THREE.Color(0xffffff);
        const cTeal = new THREE.Color(0x2dd4bf);
        const cAmber = new THREE.Color(0xfacc15);
        for (let i = 0; i < count; i++) {
            const i3 = i * 3;
            const radius = 80 + Math.random() * 90;
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos((Math.random() * 2) - 1);
            positions[i3] = radius * Math.sin(phi) * Math.cos(theta);
            positions[i3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
            positions[i3 + 2] = radius * Math.cos(phi);
            const r = Math.random();
            const col = r > 0.85 ? cTeal : (r > 0.7 ? cAmber : cWhite);
            colors[i3] = col.r;
            colors[i3 + 1] = col.g;
            colors[i3 + 2] = col.b;
        }
        geom.setAttribute("position", new THREE.BufferAttribute(positions, 3));
        geom.setAttribute("color", new THREE.BufferAttribute(colors, 3));
        const mat = new THREE.PointsMaterial({
            size: 0.85,
            vertexColors: true,
            transparent: true,
            opacity: 0.85,
            fog: false
        });
        const stars = new THREE.Points(geom, mat);
        this.scene.add(stars);
    }
    /**
     * High-Resolution NASA Earth with PBR Maps & Atmospheric Fresnel Shader
     */
    createPhotorealisticEarth() {
        this.spaceGroup = new THREE.Group();
        this.spaceGroup.position.set(0, -1.5, 0);
        const texLoader = new THREE.TextureLoader();
        const earthRadius = 4.2;
        // 1. Core Earth Sphere with NASA Maps
        const earthGeom = new THREE.SphereGeometry(earthRadius, 64, 48);
        const earthTex = texLoader.load("/static/textures/planets/earth_atmos.jpg");
        const normalTex = texLoader.load("/static/textures/planets/earth_normal.jpg");
        const specularTex = texLoader.load("/static/textures/planets/earth_specular.jpg");
        const earthMat = new THREE.MeshStandardMaterial({
            map: earthTex,
            normalMap: normalTex,
            normalScale: new THREE.Vector2(0.85, 0.85),
            roughnessMap: specularTex,
            roughness: 0.7,
            metalness: 0.15,
            emissive: 0x021612,
            emissiveIntensity: 0.25
        });
        this.earthMesh = new THREE.Mesh(earthGeom, earthMat);
        // Rotate so India & Himalayas face the initial view
        this.earthMesh.rotation.y = 1.95;
        this.earthMesh.rotation.x = 0.25;
        this.spaceGroup.add(this.earthMesh);
        // 2. Swirling Cloud Layer
        const cloudTex = texLoader.load("/static/textures/planets/earth_clouds.png");
        const cloudGeom = new THREE.SphereGeometry(earthRadius * 1.015, 64, 48);
        const cloudMat = new THREE.MeshStandardMaterial({
            map: cloudTex,
            transparent: true,
            opacity: 0.65,
            blending: THREE.NormalBlending,
            roughness: 1.0
        });
        this.cloudMesh = new THREE.Mesh(cloudGeom, cloudMat);
        this.cloudMesh.rotation.y = 1.95;
        this.spaceGroup.add(this.cloudMesh);
        // 3. Custom Atmospheric Fresnel Rayleigh/Mie Glow Shader
        const atmosGeom = new THREE.SphereGeometry(earthRadius * 1.06, 64, 48);
        const atmosMat = new THREE.ShaderMaterial({
            vertexShader: `
                varying vec3 vNormal;
                varying vec3 vPositionEye;
                void main() {
                    vNormal = normalize(normalMatrix * normal);
                    vPositionEye = (modelViewMatrix * vec4(position, 1.0)).xyz;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                varying vec3 vNormal;
                varying vec3 vPositionEye;
                void main() {
                    vec3 viewDir = normalize(-vPositionEye);
                    float rim = 1.0 - max(0.0, dot(vNormal, viewDir));
                    float glow = pow(rim, 3.2);
                    vec3 glowColor = mix(vec3(0.18, 0.83, 0.75), vec3(0.38, 0.74, 0.98), glow);
                    gl_FragColor = vec4(glowColor, glow * 0.9);
                }
            `,
            blending: THREE.AdditiveBlending,
            side: THREE.BackSide,
            transparent: true,
            depthWrite: false
        });
        this.atmosphereMesh = new THREE.Mesh(atmosGeom, atmosMat);
        this.spaceGroup.add(this.atmosphereMesh);
        // 4. Himachal Pradesh Target Beacon (31.5°N, 77.2°E)
        this.himachalBeacon = new THREE.Group();
        const phi = (90 - 31.5) * (Math.PI / 180);
        const theta = (77.2 + 180) * (Math.PI / 180);
        const bx = -(earthRadius * 1.01 * Math.sin(phi) * Math.cos(theta));
        const by = earthRadius * 1.01 * Math.cos(phi);
        const bz = earthRadius * 1.01 * Math.sin(phi) * Math.sin(theta);
        this.himachalBeacon.position.set(bx, by, bz);
        // Pulsing Concentric Rings
        const ringGeom = new THREE.RingGeometry(0.12, 0.18, 32);
        const ringMat = new THREE.MeshBasicMaterial({
            color: 0x2dd4bf,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.95
        });
        const beaconRing = new THREE.Mesh(ringGeom, ringMat);
        beaconRing.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), this.himachalBeacon.position.clone().normalize());
        this.himachalBeacon.add(beaconRing);
        // Center Pin
        const pinGeom = new THREE.SphereGeometry(0.06, 16, 16);
        const pinMat = new THREE.MeshBasicMaterial({ color: 0xfacc15 });
        const pinSphere = new THREE.Mesh(pinGeom, pinMat);
        this.himachalBeacon.add(pinSphere);
        this.earthMesh.add(this.himachalBeacon);
        this.scene.add(this.spaceGroup);
    }
    /**
     * Load Genuine 3D GLTF Spacecraft / Satellite
     */
    loadGltfSatellite() {
        const loader = new THREE.GLTFLoader();
        loader.load("/static/models/cubesat.glb", (gltf) => {
            this.satelliteModel = gltf.scene;
            this.satelliteModel.scale.set(0.8, 0.8, 0.8);
            this.satelliteModel.position.set(3.8, 4.2, 4.0);
            this.satelliteModel.rotation.set(-0.4, 0.6, 0.3);
            // Apply PBR Enhancements to loaded materials
            this.satelliteModel.traverse((node) => {
                if (node.isMesh && node.material) {
                    node.material.metalness = Math.max(0.6, node.material.metalness || 0.7);
                    node.material.roughness = Math.min(0.35, node.material.roughness || 0.3);
                    node.castShadow = true;
                }
            });
            this.scene.add(this.satelliteModel);
        }, undefined, (err) => {
            console.warn("Using procedural fallback for satellite:", err);
            this.createHighDetailFallbackSatellite();
        });
    }
    createHighDetailFallbackSatellite() {
        this.satelliteModel = new THREE.Group();
        // Gold MLI Core Bus
        const bus = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.8, 1.6), new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 0.9, roughness: 0.25 }));
        this.satelliteModel.add(bus);
        // Twin Solar Wings
        const wingMat = new THREE.MeshStandardMaterial({
            color: 0x0f3460,
            metalness: 0.85,
            roughness: 0.15,
            emissive: 0x0a2647
        });
        const leftWing = new THREE.Mesh(new THREE.BoxGeometry(3.6, 0.05, 1.0), wingMat);
        leftWing.position.x = -2.5;
        this.satelliteModel.add(leftWing);
        const rightWing = new THREE.Mesh(new THREE.BoxGeometry(3.6, 0.05, 1.0), wingMat);
        rightWing.position.x = 2.5;
        this.satelliteModel.add(rightWing);
        // SAR Antenna
        const sar = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.06, 2.8), new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: 0.5, roughness: 0.3 }));
        sar.position.y = -0.55;
        this.satelliteModel.add(sar);
        this.satelliteModel.position.set(3.8, 4.2, 4.0);
        this.scene.add(this.satelliteModel);
    }
    /**
     * InSAR Radar Volumetric Scanning Cone & Downlink Particle Stream
     */
    createInSARBeam() {
        const coneGeom = new THREE.ConeGeometry(2.6, 7.5, 32, 1, true);
        coneGeom.translate(0, -3.75, 0);
        const coneMat = new THREE.MeshBasicMaterial({
            color: 0x2dd4bf,
            transparent: true,
            opacity: 0.24,
            side: THREE.DoubleSide,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        });
        this.insarBeamMesh = new THREE.Mesh(coneGeom, coneMat);
        this.insarBeamMesh.position.set(3.8, 4.2, 4.0);
        this.insarBeamMesh.rotation.x = Math.PI / 4;
        this.scene.add(this.insarBeamMesh);
        // Data Telemetry Downlink Particles
        const pCount = 140;
        const pGeom = new THREE.BufferGeometry();
        const pPos = new Float32Array(pCount * 3);
        for (let i = 0; i < pCount; i++) {
            const i3 = i * 3;
            pPos[i3] = (Math.random() - 0.5) * 1.6;
            pPos[i3 + 1] = -Math.random() * 7.5;
            pPos[i3 + 2] = (Math.random() - 0.5) * 1.6;
        }
        pGeom.setAttribute("position", new THREE.BufferAttribute(pPos, 3));
        const pMat = new THREE.PointsMaterial({
            color: 0x5eead4,
            size: 0.14,
            transparent: true,
            opacity: 0.8,
            blending: THREE.AdditiveBlending
        });
        this.telemetryStream = new THREE.Points(pGeom, pMat);
        this.insarBeamMesh.add(this.telemetryStream);
    }
    /**
     * Hyper-Detailed 3D Himalayan Alpine Massif
     * Procedural high-relief ridges, valleys, and animated military LiDAR elevation contour scan lines.
     */
    createHimalayanMassif() {
        this.terrainGroup = new THREE.Group();
        // Positioned below space orbit (revealed during the orbital dive)
        this.terrainGroup.position.set(0, -35, 0);
        const width = 36;
        const depth = 36;
        const segX = 180;
        const segY = 180;
        const geom = new THREE.PlaneGeometry(width, depth, segX, segY);
        // Procedural Alpine Elevation Generation
        const pos = geom.attributes.position;
        for (let i = 0; i < pos.count; i++) {
            const x = pos.getX(i);
            const y = pos.getY(i);
            // Multi-frequency Perlin ridge simulation
            const d = Math.sqrt(x * x + y * y);
            const mainRidge = Math.sin(x * 0.22 + y * 0.15) * 3.8 + Math.cos(x * 0.35 - y * 0.2) * 2.4;
            const subRidge = Math.sin(x * 0.7 - y * 0.6) * 1.2 + Math.cos(x * 0.9 + y * 0.8) * 0.6;
            const valleyCarve = -Math.exp(-Math.pow(x - 2.0, 2) / 14.0) * 3.5; // River gorge cut
            const elevation = (mainRidge + subRidge + valleyCarve) * Math.max(0.2, 1.0 - d / 24.0);
            pos.setZ(i, elevation);
        }
        geom.computeVertexNormals();
        // Custom Himalayan Elevation Shader (Snow peaks, granite cliffs, pine valleys, contour lines)
        const mountainMat = new THREE.ShaderMaterial({
            uniforms: {
                uTime: { value: 0 },
                uContourSpacing: { value: 1.2 },
                uScanLineY: { value: 0 }
            },
            vertexShader: `
                varying vec3 vWorldPos;
                varying vec3 vNormal;
                varying float vElevation;
                void main() {
                    vNormal = normalize(normalMatrix * normal);
                    vec4 worldPos = modelMatrix * vec4(position, 1.0);
                    vWorldPos = worldPos.xyz;
                    vElevation = position.z;
                    gl_Position = projectionMatrix * viewMatrix * worldPos;
                }
            `,
            fragmentShader: `
                uniform float uTime;
                uniform float uContourSpacing;
                varying vec3 vWorldPos;
                varying vec3 vNormal;
                varying float vElevation;

                void main() {
                    // Elevation color zoning
                    vec3 valleyColor = vec3(0.04, 0.18, 0.14);   // Deep pine alpine
                    vec3 screeColor  = vec3(0.16, 0.22, 0.21);   // Colluvium talus rock
                    vec3 rockColor   = vec3(0.25, 0.32, 0.30);   // Exposed granite
                    vec3 snowColor   = vec3(0.92, 0.98, 0.98);   // Alpine snow

                    vec3 baseCol = valleyColor;
                    if (vElevation > 0.8) baseCol = mix(valleyColor, screeColor, (vElevation - 0.8) / 1.4);
                    if (vElevation > 2.2) baseCol = mix(screeColor, rockColor, (vElevation - 2.2) / 1.5);
                    if (vElevation > 3.7) baseCol = mix(rockColor, snowColor, (vElevation - 3.7) / 1.5);

                    // Slope shading
                    float slope = 1.0 - max(0.0, vNormal.z);
                    baseCol = mix(baseCol, rockColor * 0.8, slope * 0.7);

                    // Dynamic Neon Topographic LiDAR Contour Lines
                    float contour = mod(vElevation, uContourSpacing);
                    float line = smoothstep(0.0, 0.08, contour) - smoothstep(0.08, 0.16, contour);
                    
                    // Radar sweep pulse traveling across terrain
                    float sweep = sin(vWorldPos.y * 0.3 - uTime * 2.0);
                    sweep = smoothstep(0.92, 1.0, sweep);

                    vec3 contourColor = vec3(0.18, 0.83, 0.75); // Neon Teal
                    vec3 finalCol = mix(baseCol, contourColor, line * 0.45 + sweep * 0.65);

                    // Subtle diffuse lighting
                    vec3 lightDir = normalize(vec3(0.6, 0.8, 0.5));
                    float diff = max(0.25, dot(vNormal, lightDir));

                    gl_FragColor = vec4(finalCol * diff, 1.0);
                }
            `,
            side: THREE.DoubleSide
        });
        this.mountainMesh = new THREE.Mesh(geom, mountainMat);
        this.mountainMesh.rotation.x = -Math.PI / 2.3;
        this.terrainGroup.add(this.mountainMesh);
        // Daylighting Landslide Shear Failure Plane (Glowing Amber Cut)
        const slipGeom = new THREE.PlaneGeometry(6.5, 4.5);
        const slipMat = new THREE.MeshBasicMaterial({
            color: 0xf59e0b,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.65,
            wireframe: true
        });
        this.landslideFaultMesh = new THREE.Mesh(slipGeom, slipMat);
        this.landslideFaultMesh.position.set(3.2, 1.8, 2.5);
        this.landslideFaultMesh.rotation.set(-0.8, 0.3, 0.2);
        this.terrainGroup.add(this.landslideFaultMesh);
        // Highway Corridor Telemetry Line (NH-21 Valley Pavement)
        const roadCurve = new THREE.CatmullRomCurve3([
            new THREE.Vector3(-14, -2.8, -12),
            new THREE.Vector3(-6, -1.8, -4),
            new THREE.Vector3(2, -0.9, 4),
            new THREE.Vector3(10, 0.2, 12)
        ]);
        const roadGeom = new THREE.TubeGeometry(roadCurve, 64, 0.18, 8, false);
        const roadMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });
        this.highwayLineMesh = new THREE.Mesh(roadGeom, roadMat);
        this.terrainGroup.add(this.highwayLineMesh);
        this.scene.add(this.terrainGroup);
    }
    /**
     * GSAP & ScrollTrigger Timeline
     * Orchestrates butter-smooth cinematic transitions across 5 mission phases.
     */
    setupGsapScrollTimeline() {
        if (typeof gsap === "undefined" || typeof ScrollTrigger === "undefined") {
            console.warn("GSAP ScrollTrigger not available, falling back to manual scroll.");
            return;
        }
        gsap.registerPlugin(ScrollTrigger);
        const totalScrollHeight = document.documentElement.scrollHeight - window.innerHeight;
        // Scrubbed Master Timeline
        const tl = gsap.timeline({
            scrollTrigger: {
                trigger: ".fps-scroll-wrapper",
                start: "top top",
                end: "bottom bottom",
                scrub: 1.4, // Butter-smooth inertia
                onUpdate: (self) => {
                    this.updateNavProgressUI(self.progress);
                }
            }
        });
        // Phase 1 -> Phase 2: Zoom close to Satellite & SAR Antenna
        tl.to(this.camera.position, { x: -3.5, y: 3.8, z: 9.5, ease: "power2.inOut" }, 0.0);
        tl.to(this.spaceGroup.rotation, { y: 0.85, ease: "power2.inOut" }, 0.0);
        // Phase 2 -> Phase 3: The Orbital Dive into Atmosphere
        tl.to(this.camera.position, { x: 0.5, y: -8.0, z: 12.0, ease: "power2.inOut" }, 0.25);
        tl.to(this.spaceGroup.position, { y: 25.0, ease: "power2.inOut" }, 0.25);
        tl.to(this.spaceGroup.scale, { x: 0.2, y: 0.2, z: 0.2, ease: "power2.inOut" }, 0.25);
        tl.to(this.terrainGroup.position, { y: -2.0, ease: "power2.inOut" }, 0.25);
        // Phase 3 -> Phase 4: Fly across Himalayan Ridges & LiDAR Contours
        tl.to(this.camera.position, { x: 4.5, y: 3.5, z: 8.5, ease: "power2.inOut" }, 0.55);
        tl.to(this.terrainGroup.rotation, { y: 0.65, ease: "power2.inOut" }, 0.55);
        // Phase 4 -> Phase 5: Focus on Highway Corridor & Early Warning Hub
        tl.to(this.camera.position, { x: 1.2, y: 1.8, z: 6.2, ease: "power2.inOut" }, 0.80);
        tl.to(this.terrainGroup.rotation, { y: 1.15, ease: "power2.inOut" }, 0.80);
    }
    updateNavProgressUI(progress) {
        const sections = document.querySelectorAll(".fps-nav-section");
        const total = sections.length;
        const activeIdx = Math.min(total - 1, Math.floor(progress * total));
        if (activeIdx !== this.currentPhaseIndex) {
            this.currentPhaseIndex = activeIdx;
        }
        sections.forEach((sec, idx) => {
            const fill = sec.querySelector(".fps-progress-fill");
            if (idx < this.currentPhaseIndex) {
                sec.classList.add("completed");
                sec.classList.remove("active");
                if (fill)
                    fill.style.width = "100%";
            }
            else if (idx === this.currentPhaseIndex) {
                sec.classList.add("active");
                sec.classList.remove("completed");
                const stepSpan = 1 / total;
                const pInside = (progress - idx * stepSpan) / stepSpan;
                if (fill)
                    fill.style.width = `${Math.round(Math.max(0, Math.min(1, pInside)) * 100)}%`;
            }
            else {
                sec.classList.remove("active", "completed");
                if (fill)
                    fill.style.width = "0%";
            }
        });
        // Update Live Telemetry Pill
        const altEl = document.getElementById("telem-altitude");
        const modeEl = document.getElementById("telem-mode");
        const revEl = document.getElementById("telem-revisit");
        if (altEl && modeEl && revEl) {
            if (this.currentPhaseIndex <= 1) {
                altEl.textContent = "690 KM LEO";
                modeEl.textContent = "C-BAND SAR ACTIVE";
                revEl.textContent = "12-DAY CADENCE";
            }
            else if (this.currentPhaseIndex === 2) {
                altEl.textContent = "220 KM STRATO-DIVE";
                modeEl.textContent = "ATMOSPHERIC INGESTION";
                revEl.textContent = "IMD DOPPLER FUSION";
            }
            else if (this.currentPhaseIndex === 3) {
                altEl.textContent = "ELEV 2,845m RIDGE";
                modeEl.textContent = "LiDAR CONTOUR SCAN";
                revEl.textContent = "±0.5mm CREEP DETECT";
            }
            else {
                altEl.textContent = "NH-21 CORRIDOR";
                modeEl.textContent = "AUTONOMOUS DISPATCH";
                revEl.textContent = "EARLY WARNING CONFIRMED";
            }
        }
    }
    bindUserInteractions() {
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
        window.addEventListener("mousemove", (e) => {
            this.targetMouseX = (e.clientX / window.innerWidth) * 2 - 1;
            this.targetMouseY = -(e.clientY / window.innerHeight) * 2 + 1;
        });
        // Nav click jumps smoothly
        document.querySelectorAll(".fps-nav-section").forEach((sec, idx) => {
            sec.addEventListener("click", () => {
                const frame = document.querySelector(`.fps-frame[data-step="${idx}"]`);
                if (frame)
                    frame.scrollIntoView({ behavior: "smooth" });
            });
        });
        // HUD Bloom Toggle
        const btnBloom = document.getElementById("btn-toggle-bloom");
        if (btnBloom) {
            btnBloom.addEventListener("click", () => {
                this.isBloomEnabled = !this.isBloomEnabled;
                btnBloom.classList.toggle("active", this.isBloomEnabled);
            });
        }
    }
    /**
     * 60 FPS Render & Animation Loop
     */
    animate() {
        requestAnimationFrame(() => this.animate());
        const dt = this.clock.getDelta();
        const t = this.clock.getElapsedTime();
        // Mouse Parallax Easing
        this.mouseX += (this.targetMouseX - this.mouseX) * 0.04;
        this.mouseY += (this.targetMouseY - this.mouseY) * 0.04;
        this.camera.position.x += this.mouseX * 0.015;
        this.camera.position.y += this.mouseY * 0.015;
        // Earth Orbit & Clouds Animation
        if (this.earthMesh)
            this.earthMesh.rotation.y += 0.0008;
        if (this.cloudMesh)
            this.cloudMesh.rotation.y += 0.0011;
        // Satellite Subtle Float
        if (this.satelliteModel) {
            this.satelliteModel.rotation.y = Math.sin(t * 0.4) * 0.2 + 0.5;
            this.satelliteModel.position.y = 4.2 + Math.sin(t * 0.8) * 0.15;
        }
        // Radar Beam Pulses
        if (this.insarBeamMesh) {
            this.insarBeamMesh.material.opacity = 0.22 + Math.sin(t * 3.5) * 0.08;
        }
        // Telemetry Stream Descending Particles
        if (this.telemetryStream) {
            const arr = this.telemetryStream.geometry.attributes.position.array;
            for (let i = 1; i < arr.length; i += 3) {
                arr[i] -= 0.14;
                if (arr[i] < -7.5)
                    arr[i] = 0;
            }
            this.telemetryStream.geometry.attributes.position.needsUpdate = true;
        }
        // Himalayan Massif Shader Time Uniforms (LiDAR contour wave sweep)
        if (this.mountainMesh && this.mountainMesh.material.uniforms) {
            this.mountainMesh.material.uniforms.uTime.value = t;
        }
        // Landslide Shear Plane Warning Pulse
        if (this.landslideFaultMesh) {
            this.landslideFaultMesh.material.opacity = 0.4 + Math.sin(t * 4.0) * 0.35;
        }
        // Render with Post-Processing Bloom or standard renderer
        if (this.isBloomEnabled && this.composer) {
            this.composer.render();
        }
        else {
            this.renderer.render(this.scene, this.camera);
        }
    }
}
// Bootstrap
document.addEventListener("DOMContentLoaded", () => {
    new SatelliteServiceApp();
});
