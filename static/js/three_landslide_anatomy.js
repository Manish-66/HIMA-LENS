/**
 * ============================================================================
 * HIMA-LENS: 3D Landslide Failure Anatomy & Kinematics Simulator (Three.js)
 * Compliant with USGS Circular 1325 (Highland & Bobrowsky) & Cruden-Varnes (1996)
 * ============================================================================
 */

(function () {
    'use strict';

    // State & Configurations
    const state = {
        showGroundwater: true,
        showStabilization: false,
        showPins: true,
        isWireframe: false,
        autoRotate: true,
        activePinId: 1,
        cameraPreset: 'perspective'
    };

    // Pin Data & Geological Definitions
    const ANATOMY_PINS = [
        {
            id: 1,
            title: "Crown Tension Cracks",
            kicker: "USGS ANATOMICAL FEATURE 01",
            coords: { x: -3.8, y: 5.2, z: -1.2 },
            cameraPos: { x: -6, y: 8, z: 6 },
            params: {
                movement: "Incipient Shear",
                aperture: "15 to 45 mm",
                fosImpact: "FOS drops 25%",
                usgsClass: "Tension Fissure Array"
            },
            desc: "Extensional tensile fractures opening along the crest uphill of the detachment scarp. Indicates active loss of lateral confinement and imminent secondary slide retrocession.",
            formula: "\\sigma_t \\le \\gamma \\cdot z \\cdot (1 - K_0)"
        },
        {
            id: 2,
            title: "Main Detachment Scarp",
            kicker: "USGS ANATOMICAL FEATURE 02",
            coords: { x: -1.5, y: 3.8, z: -0.5 },
            cameraPos: { x: -4, y: 6, z: 9 },
            params: {
                movement: "Translational Cleavage",
                scarpHeight: "4.8 meters",
                scarpAngle: "68° Steep Cut",
                usgsClass: "Main Scarp Face"
            },
            desc: "A steep surface on the undisturbed ground around the periphery of the landslide, caused by the downward movement of displaced rock and colluvial regolith under gravity.",
            formula: "H_{crit} = \\frac{4c'}{\\gamma} \\tan(45° + \\phi'/2)"
        },
        {
            id: 3,
            title: "Rupture Surface / Slip Plane",
            kicker: "USGS ANATOMICAL FEATURE 03",
            coords: { x: 0.2, y: 1.8, z: 0.2 },
            cameraPos: { x: -9, y: 2, z: 0 },
            params: {
                movement: "Planar Shear Daylighting",
                dipAngle: "34° Daylighting",
                cohesion: "c' = 18 kPa",
                friction: "\\phi' = 28°"
            },
            desc: "The basal shear plane along which the mass slides outward and downward. In Himalayan sandstone, often governed by daylighting relict bedding joints lubricated by high pore pressure.",
            formula: "FOS = \\frac{c' + (\\sigma_n - u)\\tan\\phi'}{\\tau_d}"
        },
        {
            id: 4,
            title: "Accumulation Toe & Road Blockage",
            kicker: "USGS ANATOMICAL FEATURE 04",
            coords: { x: 2.4, y: 0.2, z: 1.5 },
            cameraPos: { x: 4, y: 3, z: 8 },
            params: {
                movement: "Corridor Inundation",
                debrisVolume: "175 m³ Displaced",
                roadBlock: "100% Carriageway",
                clearanceRate: "MoRTH 301.1"
            },
            desc: "The margin of the displaced material most distant from the main scarp. The toe overrides the road pavement, crushing roadside drainage and severing hill transportation routes.",
            formula: "V_{debris} = L_{toe} \\cdot W_{cway} \\cdot H_{pile}"
        },
        {
            id: 5,
            title: "Engineered Stabilization System",
            kicker: "HPPWD & CEDD GEOGUIDE 7",
            coords: { x: 1.2, y: 0.8, z: 0.6 },
            cameraPos: { x: 3, y: 4, z: 7 },
            params: {
                countermeasure: "Plum Wall + Soil Nails",
                wallHeight: "H = 3.2 m (M15 Plum)",
                nailGrid: "2.0m x 2.0m Staggered",
                targetFos: "FOS ≥ 1.30 (Safe)"
            },
            desc: "Composite retention system combining a gravity plum concrete breast wall at the toe with high-yield deformed steel soil nails (Fe500, 25mm dia) anchored into competent bedrock.",
            formula: "FOS_{stabilized} = FOS_0 + \\frac{T_{nail} \\cdot (\\cos\\theta + \\sin\\theta\\tan\\phi')}{W\\sin\\theta}"
        }
    ];

    // Three.js variables
    let scene, camera, renderer, controls;
    let terrainGroup, groundwaterMesh, waterParticles, stabilizationGroup;
    let pinElements = [];
    let isIntersecting = false;
    let animFrameId = null;

    // Procedural Geological Texture Generator
    function createGeologicalTexture() {
        const canvas = document.createElement('canvas');
        canvas.width = 512;
        canvas.height = 512;
        const ctx = canvas.getContext('2d');

        // Base gradient
        const grad = ctx.createLinearGradient(0, 0, 0, 512);
        grad.addColorStop(0, '#785b3a');   // Colluvium / soil top
        grad.addColorStop(0.3, '#5c4832'); // Weathered layer
        grad.addColorStop(0.32, '#2f3b37');// Sandstone transition
        grad.addColorStop(0.7, '#242e2b'); // Compact sandstone
        grad.addColorStop(1, '#171e1c');   // Deep bedrock
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, 512, 512);

        // Sedimentary stratification lines
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
        ctx.lineWidth = 1.5;
        for (let y = 160; y < 512; y += 12) {
            ctx.beginPath();
            ctx.moveTo(0, y + (Math.sin(y * 0.1) * 3));
            for (let x = 0; x <= 512; x += 32) {
                ctx.lineTo(x, y + (Math.sin(x * 0.03 + y * 0.05) * 4));
            }
            ctx.stroke();
        }

        // Cross-bedding fractures
        ctx.strokeStyle = 'rgba(15, 23, 42, 0.25)';
        ctx.lineWidth = 1;
        for (let i = 0; i < 40; i++) {
            const rx = Math.random() * 512;
            const ry = 180 + Math.random() * 300;
            ctx.beginPath();
            ctx.moveTo(rx, ry);
            ctx.lineTo(rx + 25, ry + 35);
            ctx.stroke();
        }

        const texture = new THREE.CanvasTexture(canvas);
        texture.wrapS = THREE.RepeatWrapping;
        texture.wrapT = THREE.RepeatWrapping;
        return texture;
    }

    // Initialize 3D Scene
    function initThreeScene() {
        const container = document.getElementById('three-canvas-container');
        if (!container || !window.THREE) return;

        const width = container.clientWidth || 600;
        const height = container.clientHeight || 520;

        // Scene
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0x041a14);
        scene.fog = new THREE.FogExp2(0x041a14, 0.035);

        // Camera
        camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 100);
        camera.position.set(-8, 7.5, 12);

        // Renderer
        renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
        renderer.setSize(width, height);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        container.appendChild(renderer.domElement);

        // OrbitControls
        if (window.THREE.OrbitControls) {
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.06;
            controls.maxDistance = 25;
            controls.minDistance = 5;
            controls.maxPolarAngle = Math.PI / 2 - 0.02; // Don't go below ground
            controls.target.set(0, 2, 0);
        }

        // Lighting
        setupLighting();

        // Build 3D Geological Models
        buildGeologicalModels();

        // Build 3D Hotspot Pins
        createHtmlPinMarkers(container);

        // Setup DOM Events
        bindDomControls();

        // Viewport Resize Observer
        window.addEventListener('resize', onWindowResize);

        // Performance Optimization: IntersectionObserver
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                isIntersecting = entry.isIntersecting;
                if (isIntersecting && !animFrameId) {
                    animate();
                }
            });
        }, { threshold: 0.1 });
        observer.observe(container);

        // Initial Inspector Update
        updateInspectorCard(ANATOMY_PINS[0]);
    }

    function setupLighting() {
        // Ambient Light
        const ambientLight = new THREE.AmbientLight(0xd4f7eb, 0.6);
        scene.add(ambientLight);

        // Main Himalayan Sunlight (Warm Directional)
        const sunLight = new THREE.DirectionalLight(0xfff7ed, 1.2);
        sunLight.position.set(12, 18, 10);
        sunLight.castShadow = true;
        sunLight.shadow.mapSize.width = 1024;
        sunLight.shadow.mapSize.height = 1024;
        sunLight.shadow.bias = -0.0005;
        scene.add(sunLight);

        // Fill Light (Cool Teal Rim Light)
        const fillLight = new THREE.DirectionalLight(0x2dd4bf, 0.5);
        fillLight.position.set(-10, 6, -8);
        scene.add(fillLight);

        // Ground Bounce Light
        const hemiLight = new THREE.HemisphereLight(0x5eead4, 0x051b15, 0.4);
        scene.add(hemiLight);
    }

    function buildGeologicalModels() {
        terrainGroup = new THREE.Group();
        scene.add(terrainGroup);

        const geoTexture = createGeologicalTexture();

        // Materials
        const bedrockMat = new THREE.MeshStandardMaterial({
            map: geoTexture,
            roughness: 0.75,
            metalness: 0.1,
            flatShading: true
        });

        const colluviumMat = new THREE.MeshStandardMaterial({
            color: 0x8a6e4b,
            roughness: 0.9,
            metalness: 0.05,
            flatShading: true
        });

        const asphaltMat = new THREE.MeshStandardMaterial({
            color: 0x1e293b,
            roughness: 0.7,
            metalness: 0.2
        });

        const slipPlaneMat = new THREE.MeshStandardMaterial({
            color: 0x991b1b,
            roughness: 0.4,
            metalness: 0.2,
            side: THREE.DoubleSide
        });

        // 1. STABLE BEDROCK BLOCK (Extruded Mountain Cut)
        const bedrockShape = new THREE.Shape();
        bedrockShape.moveTo(-5, 0);
        bedrockShape.lineTo(5, 0);
        bedrockShape.lineTo(5, 1.2);
        bedrockShape.lineTo(1.5, 1.2);   // Road outer edge
        bedrockShape.lineTo(0.5, 1.2);   // Road inner toe
        bedrockShape.lineTo(-2.5, 4.2);  // Cut slope
        bedrockShape.lineTo(-5, 5.8);    // Uphill crest
        bedrockShape.closePath();

        const extrudeSettings = { depth: 5, bevelEnabled: true, bevelSegments: 2, steps: 1, bevelSize: 0.1, bevelThickness: 0.1 };
        const bedrockGeo = new THREE.ExtrudeGeometry(bedrockShape, extrudeSettings);
        bedrockGeo.center();
        const bedrockMesh = new THREE.Mesh(bedrockGeo, bedrockMat);
        bedrockMesh.position.set(0, 2.4, 0);
        bedrockMesh.receiveShadow = true;
        bedrockMesh.castShadow = true;
        terrainGroup.add(bedrockMesh);

        // 2. ROAD CARRIAGEWAY PAVEMENT
        const roadGeo = new THREE.BoxGeometry(1.6, 0.08, 5.1);
        const roadMesh = new THREE.Mesh(roadGeo, asphaltMat);
        roadMesh.position.set(1.15, 1.24, 0);
        roadMesh.receiveShadow = true;
        terrainGroup.add(roadMesh);

        // Road center dashed line
        const lineGeo = new THREE.BoxGeometry(0.08, 0.09, 5.0);
        const lineMat = new THREE.MeshBasicMaterial({ color: 0xfacc15 });
        const lineMesh = new THREE.Mesh(lineGeo, lineMat);
        lineMesh.position.set(1.15, 1.25, 0);
        terrainGroup.add(lineMesh);

        // 3. COLLUVIAL REGOLITH CAP (Upper Slope)
        const capGeo = new THREE.BoxGeometry(3.2, 0.25, 5.1);
        const capMesh = new THREE.Mesh(capGeo, colluviumMat);
        capMesh.position.set(-3.7, 5.15, 0);
        capMesh.rotation.z = -0.32;
        capMesh.receiveShadow = true;
        terrainGroup.add(capMesh);

        // 4. DAYLIGHTING RUPTURE SURFACE (Red Shear Plane)
        const ruptureGeo = new THREE.PlaneGeometry(3.6, 4.9);
        const ruptureMesh = new THREE.Mesh(ruptureGeo, slipPlaneMat);
        ruptureMesh.position.set(-0.8, 2.7, 0);
        ruptureMesh.rotation.y = Math.PI / 2;
        ruptureMesh.rotation.x = Math.PI / 2 - 0.78;
        terrainGroup.add(ruptureMesh);

        // 5. DISPLACED LANDSLIDE DEBRIS ACCUMULATION (Toe Rubble at Road)
        const debrisGroup = new THREE.Group();
        const debrisColors = [0x785b3a, 0x5c4832, 0x475569, 0x334155];
        for (let i = 0; i < 28; i++) {
            const size = 0.15 + Math.random() * 0.35;
            const bGeo = new THREE.DodecahedronGeometry(size, 0);
            const bMat = new THREE.MeshStandardMaterial({
                color: debrisColors[Math.floor(Math.random() * debrisColors.length)],
                roughness: 0.85,
                flatShading: true
            });
            const boulder = new THREE.Mesh(bGeo, bMat);
            boulder.position.set(
                0.7 + Math.random() * 1.1,
                1.3 + Math.random() * 0.45,
                -2.2 + Math.random() * 4.4
            );
            boulder.rotation.set(Math.random() * 3, Math.random() * 3, Math.random() * 3);
            boulder.castShadow = true;
            boulder.receiveShadow = true;
            debrisGroup.add(boulder);
        }
        terrainGroup.add(debrisGroup);

        // 6. CROWN TENSION CRACKS (Fissure Geometry)
        const crackMat = new THREE.MeshBasicMaterial({ color: 0x091410 });
        for (let j = 0; j < 5; j++) {
            const crackGeo = new THREE.BoxGeometry(0.12, 0.4, 0.9 + Math.random() * 0.6);
            const crackMesh = new THREE.Mesh(crackGeo, crackMat);
            crackMesh.position.set(-3.6 - Math.random() * 0.5, 5.2, -1.8 + j * 0.9);
            crackMesh.rotation.y = (Math.random() - 0.5) * 0.4;
            terrainGroup.add(crackMesh);
        }

        // 7. GROUNDWATER / PHREATIC SEEPAGE PLANE (Animated Cyan Flow)
        buildGroundwaterSystem();

        // 8. 3D STABILIZATION COUNTERMEASURES (Plum Wall & Soil Nails)
        buildStabilizationSystem();
    }

    function buildGroundwaterSystem() {
        const waterGeo = new THREE.PlaneGeometry(3.4, 4.8);
        const waterMat = new THREE.MeshStandardMaterial({
            color: 0x38bdf8,
            roughness: 0.1,
            metalness: 0.2,
            transparent: true,
            opacity: 0.45,
            side: THREE.DoubleSide
        });
        groundwaterMesh = new THREE.Mesh(waterGeo, waterMat);
        groundwaterMesh.position.set(-0.9, 2.5, 0);
        groundwaterMesh.rotation.y = Math.PI / 2;
        groundwaterMesh.rotation.x = Math.PI / 2 - 0.78;
        terrainGroup.add(groundwaterMesh);

        // Particle stream for daylighting seepage
        const pCount = 60;
        const pGeo = new THREE.BufferGeometry();
        const positions = new Float32Array(pCount * 3);
        for (let i = 0; i < pCount * 3; i += 3) {
            positions[i] = 0.5 + (Math.random() - 0.5) * 0.6;   // X
            positions[i + 1] = 1.3 + Math.random() * 1.5;       // Y
            positions[i + 2] = -2.2 + Math.random() * 4.4;      // Z
        }
        pGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));

        const pMat = new THREE.PointsMaterial({
            color: 0x2dd4bf,
            size: 0.08,
            transparent: true,
            opacity: 0.75
        });
        waterParticles = new THREE.Points(pGeo, pMat);
        terrainGroup.add(waterParticles);
    }

    function buildStabilizationSystem() {
        stabilizationGroup = new THREE.Group();
        stabilizationGroup.visible = state.showStabilization;
        terrainGroup.add(stabilizationGroup);

        // 1. PLUM CONCRETE BREAST WALL AT TOE (HPPWD HPSOR 4.2 / MoRTH 1402)
        const wallShape = new THREE.Shape();
        wallShape.moveTo(0, 0);
        wallShape.lineTo(0.9, 0);       // Base width 0.9m
        wallShape.lineTo(0.4, 1.4);     // Top width 0.4m, Height 1.4m
        wallShape.lineTo(0, 1.4);
        wallShape.closePath();

        const wallExtrude = { depth: 5.1, bevelEnabled: true, bevelSize: 0.04, bevelThickness: 0.04 };
        const wallGeo = new THREE.ExtrudeGeometry(wallShape, wallExtrude);
        wallGeo.center();

        const concreteMat = new THREE.MeshStandardMaterial({
            color: 0x64748b,
            roughness: 0.8,
            metalness: 0.15
        });
        const wallMesh = new THREE.Mesh(wallGeo, concreteMat);
        wallMesh.position.set(0.65, 1.9, 0);
        wallMesh.castShadow = true;
        wallMesh.receiveShadow = true;
        stabilizationGroup.add(wallMesh);

        // Wall Drainage Weep Holes
        const weepMat = new THREE.MeshBasicMaterial({ color: 0x0f172a });
        for (let wz = -2.1; wz <= 2.1; wz += 0.8) {
            for (let wy of [1.5, 2.1]) {
                const weepGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.7, 8);
                const weepMesh = new THREE.Mesh(weepGeo, weepMat);
                weepMesh.position.set(0.7, wy, wz);
                weepMesh.rotation.z = Math.PI / 2;
                stabilizationGroup.add(weepMesh);
            }
        }

        // 2. PRESCRIBED SOIL NAILING ARRAY (CEDD Geoguide 7 - 25mm Rebar in 100mm Grout)
        const nailMat = new THREE.MeshStandardMaterial({ color: 0xd97706, metalness: 0.85, roughness: 0.3 });
        const plateMat = new THREE.MeshStandardMaterial({ color: 0x092f25, metalness: 0.4, roughness: 0.5 });

        for (let row = 0; row < 3; row++) {
            const ny = 2.4 + row * 0.9;
            const nx = -1.0 - row * 0.7;
            for (let col = -2.0; col <= 2.0; col += 0.9) {
                // Soil nail bar (penetrates deep through failure plane)
                const nailGeo = new THREE.CylinderGeometry(0.03, 0.03, 3.2, 8);
                const nailMesh = new THREE.Mesh(nailGeo, nailMat);
                nailMesh.position.set(nx - 0.8, ny - 0.3, col);
                nailMesh.rotation.z = -0.32; // 18° downward rake
                stabilizationGroup.add(nailMesh);

                // Square Bearing Head Plate (200mm x 200mm)
                const plateGeo = new THREE.BoxGeometry(0.04, 0.28, 0.28);
                const plateMesh = new THREE.Mesh(plateGeo, plateMat);
                plateMesh.position.set(nx + 0.5, ny + 0.15, col);
                plateMesh.rotation.z = -0.32;
                stabilizationGroup.add(plateMesh);
            }
        }
    }

    // Hotspot Pin HTML Elements mapped to 3D space
    function createHtmlPinMarkers(container) {
        ANATOMY_PINS.forEach((pin, idx) => {
            const marker = document.createElement('div');
            marker.className = `anatomy-pin-marker ${idx === 0 ? 'active' : ''}`;
            marker.textContent = pin.id;
            marker.setAttribute('data-id', pin.id);
            marker.title = pin.title;

            marker.addEventListener('click', (e) => {
                e.stopPropagation();
                selectPin(pin.id);
            });

            container.appendChild(marker);
            pinElements.push({ marker, pin });
        });
    }

    function selectPin(pinId) {
        const found = ANATOMY_PINS.find(p => p.id === pinId);
        if (!found) return;

        state.activePinId = pinId;

        // Update Pin DOM markers
        pinElements.forEach(item => {
            if (item.pin.id === pinId) {
                item.marker.classList.add('active');
            } else {
                item.marker.classList.remove('active');
            }
        });

        // Smooth Camera Transition to focus on pin
        if (found.cameraPos && camera && controls) {
            smoothCameraMove(found.cameraPos, found.coords);
        }

        // Update Sidebar Diagnostics Card
        updateInspectorCard(found);
    }

    function updateInspectorCard(pin) {
        const kickerEl = document.getElementById('inspector-kicker');
        const titleEl = document.getElementById('inspector-title');
        const descEl = document.getElementById('inspector-desc');
        const formulaEl = document.getElementById('inspector-formula');
        const gridEl = document.getElementById('inspector-params');

        if (kickerEl) kickerEl.textContent = pin.kicker;
        if (titleEl) titleEl.textContent = pin.title;
        if (descEl) descEl.textContent = pin.desc;
        if (formulaEl) formulaEl.textContent = pin.formula;

        if (gridEl && pin.params) {
            gridEl.innerHTML = '';
            Object.entries(pin.params).forEach(([key, val]) => {
                const pill = document.createElement('div');
                pill.className = 'param-pill';
                const label = key.replace(/([A-Z])/g, ' $1').toUpperCase();
                pill.innerHTML = `
                    <div class="param-lbl">${label}</div>
                    <div class="param-val ${key.includes('fos') || key.includes('target') ? 'accent-green' : (key.includes('movement') ? 'accent-amber' : 'accent-cyan')}">${val}</div>
                `;
                gridEl.appendChild(pill);
            });
        }
    }

    function smoothCameraMove(targetCam, targetLookAt) {
        if (!camera || !controls) return;
        const startPos = camera.position.clone();
        const startLook = controls.target.clone();
        const endPos = new THREE.Vector3(targetCam.x, targetCam.y, targetCam.z);
        const endLook = new THREE.Vector3(targetLookAt.x, targetLookAt.y, targetLookAt.z);

        const startTime = performance.now();
        const duration = 800; // ms

        function step(now) {
            const elapsed = now - startTime;
            const progress = Math.min(1, elapsed / duration);
            const ease = 1 - Math.pow(1 - progress, 3); // ease-out cubic

            camera.position.lerpVectors(startPos, endPos, ease);
            controls.target.lerpVectors(startLook, endLook, ease);
            controls.update();

            if (progress < 1) {
                requestAnimationFrame(step);
            }
        }
        requestAnimationFrame(step);
    }

    function bindDomControls() {
        // Toggle Groundwater
        const btnWater = document.getElementById('btn-toggle-water');
        if (btnWater) {
            btnWater.addEventListener('click', () => {
                state.showGroundwater = !state.showGroundwater;
                btnWater.classList.toggle('active', state.showGroundwater);
                if (groundwaterMesh) groundwaterMesh.visible = state.showGroundwater;
                if (waterParticles) waterParticles.visible = state.showGroundwater;
            });
        }

        // Toggle Stabilization
        const btnStab = document.getElementById('btn-toggle-stabilization');
        if (btnStab) {
            btnStab.addEventListener('click', () => {
                state.showStabilization = !state.showStabilization;
                btnStab.classList.toggle('active', state.showStabilization);
                if (stabilizationGroup) stabilizationGroup.visible = state.showStabilization;
                if (state.showStabilization) {
                    selectPin(5); // Focus on stabilization pin
                }
            });
        }

        // Toggle Pins
        const btnPins = document.getElementById('btn-toggle-pins');
        if (btnPins) {
            btnPins.addEventListener('click', () => {
                state.showPins = !state.showPins;
                btnPins.classList.toggle('active', state.showPins);
                pinElements.forEach(item => {
                    item.marker.style.display = state.showPins ? 'flex' : 'none';
                });
            });
        }

        // Toggle Wireframe
        const btnWire = document.getElementById('btn-toggle-wireframe');
        if (btnWire) {
            btnWire.addEventListener('click', () => {
                state.isWireframe = !state.isWireframe;
                btnWire.classList.toggle('active', state.isWireframe);
                if (terrainGroup) {
                    terrainGroup.traverse(child => {
                        if (child.isMesh && child.material) {
                            child.material.wireframe = state.isWireframe;
                        }
                    });
                }
            });
        }

        // Camera Presets
        const camBtns = document.querySelectorAll('.cam-preset-btn');
        camBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                camBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const preset = btn.getAttribute('data-preset');
                applyCameraPreset(preset);
            });
        });

        // Auto-Rotate Toggle
        const btnRotate = document.getElementById('btn-toggle-rotate');
        if (btnRotate) {
            btnRotate.addEventListener('click', () => {
                state.autoRotate = !state.autoRotate;
                btnRotate.classList.toggle('active', state.autoRotate);
            });
        }
    }

    function applyCameraPreset(preset) {
        state.cameraPreset = preset;
        switch (preset) {
            case 'cross-section':
                smoothCameraMove({ x: -11, y: 2.5, z: 0 }, { x: 0, y: 2.5, z: 0 });
                break;
            case 'overhead':
                smoothCameraMove({ x: 0, y: 14, z: 0.1 }, { x: 0, y: 0, z: 0 });
                break;
            case 'toe':
                smoothCameraMove({ x: 5, y: 3, z: 6 }, { x: 1, y: 1.5, z: 0 });
                break;
            case 'perspective':
            default:
                smoothCameraMove({ x: -8, y: 7.5, z: 12 }, { x: 0, y: 2, z: 0 });
                break;
        }
    }

    // Update 3D Pins in Screen Coordinates
    function updatePinPositions() {
        if (!state.showPins || !camera || !renderer) return;

        const container = document.getElementById('three-canvas-container');
        if (!container) return;
        const w = container.clientWidth;
        const h = container.clientHeight;

        const tempVec = new THREE.Vector3();

        pinElements.forEach(item => {
            const { marker, pin } = item;
            tempVec.set(pin.coords.x, pin.coords.y, pin.coords.z);

            // Project to normalized device space (-1 to +1)
            tempVec.project(camera);

            // Check if pin is in front of camera
            if (tempVec.z > 1) {
                marker.style.opacity = '0';
                marker.style.pointerEvents = 'none';
                return;
            }

            // Convert to CSS pixels
            const x = (tempVec.x * 0.5 + 0.5) * w;
            const y = (-(tempVec.y * 0.5) + 0.5) * h;

            marker.style.transform = `translate(${x}px, ${y}px) translate(-50%, -50%)`;
            marker.style.opacity = '1';
            marker.style.pointerEvents = 'auto';
        });
    }

    function onWindowResize() {
        const container = document.getElementById('three-canvas-container');
        if (!container || !renderer || !camera) return;

        const width = container.clientWidth;
        const height = container.clientHeight;

        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
    }

    // 60 FPS Render Loop
    function animate() {
        if (!isIntersecting) {
            animFrameId = null;
            return;
        }

        animFrameId = requestAnimationFrame(animate);

        // Auto-orbit
        if (state.autoRotate && terrainGroup) {
            terrainGroup.rotation.y += 0.003;
        }

        // Animate water seepage particles
        if (waterParticles && state.showGroundwater) {
            const pos = waterParticles.geometry.attributes.position.array;
            for (let i = 1; i < pos.length; i += 3) {
                pos[i] -= 0.015; // Flow downwards
                if (pos[i] < 1.1) {
                    pos[i] = 2.8; // Reset to crest
                }
            }
            waterParticles.geometry.attributes.position.needsUpdate = true;
        }

        if (controls) {
            controls.update();
        }

        renderer.render(scene, camera);

        // Update Pin 2D overlays
        updatePinPositions();
    }

    // Auto-bootstrap when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initThreeScene);
    } else {
        initThreeScene();
    }

})();
