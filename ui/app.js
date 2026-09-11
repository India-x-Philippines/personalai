/**
 * F.R.I.D.A.Y. — Personal AI Assistant Engine
 * Three.js 3D Geodesic Constellation Sun & Lens Flare Beam
 * Matching Cinematic Reference Image
 */

// Global Three.js Variables
let scene, camera, renderer;
let constellationNodes, lineSegmentsMesh, outerDust;
let floorGrid, flareBeamMesh;
let nodePositions = [];
let nodeVelocities = [];

const NUM_NODES = 240;
const CONNECT_DISTANCE = 13.5;

// Audio Variables
let audioCtx, analyser, dataArray, micStream;
let micActive = false;

// Right Audio Visualizer Canvas
const rightCanvas = document.getElementById('right-audio-canvas');
const rightCtx = rightCanvas ? rightCanvas.getContext('2d') : null;

// Clock Updater
function updateClock() {
    const clockEl = document.getElementById('clock-time');
    const now = new Date();
    const h = String(now.getHours()).padStart(2, '0');
    const m = String(now.getMinutes()).padStart(2, '0');
    if (clockEl) clockEl.innerText = `${h}:${m}`;
}

// Particle Glow Texture Generator
function createParticleTexture() {
    const canvas = document.createElement('canvas');
    canvas.width = 64;
    canvas.height = 64;
    const ctx = canvas.getContext('2d');

    const gradient = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
    gradient.addColorStop(0, 'rgba(255, 255, 255, 1.0)');
    gradient.addColorStop(0.2, 'rgba(255, 180, 50, 0.9)');
    gradient.addColorStop(0.6, 'rgba(255, 100, 0, 0.3)');
    gradient.addColorStop(1, 'rgba(255, 50, 0, 0)');

    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 64, 64);

    return new THREE.CanvasTexture(canvas);
}

// Initialize 3D Scene
function initScene() {
    const container = document.getElementById('canvas-container');

    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x020203, 0.005);

    camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 2, 70);

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor(0x020203);
    container.appendChild(renderer.domElement);

    const texture = createParticleTexture();

    // 1. CENTRAL INTENSE POINT LIGHT & CORE SPHERE
    const coreLight = new THREE.PointLight(0xffaa00, 3, 100);
    coreLight.position.set(0, 0, 0);
    scene.add(coreLight);

    // Inner Core Particle Cluster
    const coreGeo = new THREE.BufferGeometry();
    const coreCount = 4000;
    const corePos = new Float32Array(coreCount * 3);
    for (let i = 0; i < coreCount; i++) {
        const u = Math.random();
        const v = Math.random();
        const theta = u * 2.0 * Math.PI;
        const phi = Math.acos(2.0 * v - 1.0);
        const radius = 6 + (Math.random() - 0.5) * 4;

        corePos[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
        corePos[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
        corePos[i * 3 + 2] = radius * Math.cos(phi);
    }
    coreGeo.setAttribute('position', new THREE.BufferAttribute(corePos, 3));
    const coreMat = new THREE.PointsMaterial({
        size: 1.8,
        map: texture,
        transparent: true,
        blending: THREE.AdditiveBlending,
        color: 0xffcc44,
        depthWrite: false
    });
    scene.add(new THREE.Points(coreGeo, coreMat));

    // 2. 3D GEODESIC CONSTELLATION NODE LATTICE
    const sphereRadius = 16;
    for (let i = 0; i < NUM_NODES; i++) {
        const u = Math.random();
        const v = Math.random();
        const theta = u * 2.0 * Math.PI;
        const phi = Math.acos(2.0 * v - 1.0);
        const r = sphereRadius + (Math.random() - 0.5) * 2;

        const x = r * Math.sin(phi) * Math.cos(theta);
        const y = r * Math.sin(phi) * Math.sin(theta);
        const z = r * Math.cos(phi);

        nodePositions.push(new THREE.Vector3(x, y, z));
        nodeVelocities.push(new THREE.Vector3(
            (Math.random() - 0.5) * 0.03,
            (Math.random() - 0.5) * 0.03,
            (Math.random() - 0.5) * 0.03
        ));
    }

    // Node Point Cloud
    const nodeGeo = new THREE.BufferGeometry();
    const nodePosArr = new Float32Array(NUM_NODES * 3);
    for (let i = 0; i < NUM_NODES; i++) {
        nodePosArr[i * 3] = nodePositions[i].x;
        nodePosArr[i * 3 + 1] = nodePositions[i].y;
        nodePosArr[i * 3 + 2] = nodePositions[i].z;
    }
    nodeGeo.setAttribute('position', new THREE.BufferAttribute(nodePosArr, 3));
    const nodeMat = new THREE.PointsMaterial({
        size: 2.2,
        map: texture,
        transparent: true,
        blending: THREE.AdditiveBlending,
        color: 0xffaa00,
        depthWrite: false
    });
    const nodePoints = new THREE.Points(nodeGeo, nodeMat);
    scene.add(nodePoints);
    constellationNodes = nodePoints;

    // Line Segments for Constellation Connections
    const lineMat = new THREE.LineBasicMaterial({
        color: 0xff7700,
        transparent: true,
        opacity: 0.45,
        blending: THREE.AdditiveBlending
    });
    const maxLineSegments = NUM_NODES * NUM_NODES;
    const lineGeo = new THREE.BufferGeometry();
    const linePosArr = new Float32Array(maxLineSegments * 6);
    lineGeo.setAttribute('position', new THREE.BufferAttribute(linePosArr, 3));

    lineSegmentsMesh = new THREE.LineSegments(lineGeo, lineMat);
    scene.add(lineSegmentsMesh);

    // 3. HORIZONTAL ANAMORPHIC LENS FLARE BEAM
    const flareGeo = new THREE.PlaneGeometry(160, 0.6);
    const flareMat = new THREE.MeshBasicMaterial({
        color: 0xffaa00,
        transparent: true,
        opacity: 0.65,
        blending: THREE.AdditiveBlending,
        side: THREE.DoubleSide
    });
    flareBeamMesh = new THREE.Mesh(flareGeo, flareMat);
    scene.add(flareBeamMesh);

    // 4. OUTER RADIATING STARDUST FIELD
    const dustGeo = new THREE.BufferGeometry();
    const dustCount = 6000;
    const dustPos = new Float32Array(dustCount * 3);
    for (let i = 0; i < dustCount; i++) {
        const r = 18 + Math.random() * 45;
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.random() * Math.PI;

        dustPos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
        dustPos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
        dustPos[i * 3 + 2] = r * Math.cos(phi);
    }
    dustGeo.setAttribute('position', new THREE.BufferAttribute(dustPos, 3));
    const dustMat = new THREE.PointsMaterial({
        size: 1.0,
        map: texture,
        transparent: true,
        opacity: 0.5,
        color: 0xff8800,
        blending: THREE.AdditiveBlending,
        depthWrite: false
    });
    outerDust = new THREE.Points(dustGeo, dustMat);
    scene.add(outerDust);

    // 5. FLOOR CIRCUIT GRID & LIGHT REFLECTION POOL
    floorGrid = new THREE.GridHelper(180, 50, 0xff7700, 0x331a00);
    floorGrid.position.y = -26;
    floorGrid.material.opacity = 0.25;
    floorGrid.material.transparent = true;
    scene.add(floorGrid);

    // Light Reflection Circle on Floor
    const floorReflectGeo = new THREE.CircleGeometry(16, 32);
    const floorReflectMat = new THREE.MeshBasicMaterial({
        color: 0xff6600,
        transparent: true,
        opacity: 0.15,
        blending: THREE.AdditiveBlending,
        side: THREE.DoubleSide
    });
    const floorReflect = new THREE.Mesh(floorReflectGeo, floorReflectMat);
    floorReflect.rotation.x = Math.PI / 2;
    floorReflect.position.y = -25.9;
    scene.add(floorReflect);

    window.addEventListener('resize', onWindowResize);
}

// Update Constellation Lines Matrix
function updateConstellation(time) {
    const linePosArr = lineSegmentsMesh.geometry.attributes.position.array;
    let lineIdx = 0;

    // Move Node positions slowly around sphere radius
    for (let i = 0; i < NUM_NODES; i++) {
        nodePositions[i].add(nodeVelocities[i]);

        // Keep inside spherical boundary shell
        const dist = nodePositions[i].length();
        if (dist < 14 || dist > 18) {
            nodeVelocities[i].negate();
        }
    }

    // Update Node Point Positions
    const nodePosArr = constellationNodes.geometry.attributes.position.array;
    for (let i = 0; i < NUM_NODES; i++) {
        nodePosArr[i * 3] = nodePositions[i].x;
        nodePosArr[i * 3 + 1] = nodePositions[i].y;
        nodePosArr[i * 3 + 2] = nodePositions[i].z;
    }
    constellationNodes.geometry.attributes.position.needsUpdate = true;

    // Connect Neighboring Nodes with Line Segments
    for (let i = 0; i < NUM_NODES; i++) {
        for (let j = i + 1; j < NUM_NODES; j++) {
            const distance = nodePositions[i].distanceTo(nodePositions[j]);

            if (distance < CONNECT_DISTANCE) {
                linePosArr[lineIdx++] = nodePositions[i].x;
                linePosArr[lineIdx++] = nodePositions[i].y;
                linePosArr[lineIdx++] = nodePositions[i].z;

                linePosArr[lineIdx++] = nodePositions[j].x;
                linePosArr[lineIdx++] = nodePositions[j].y;
                linePosArr[lineIdx++] = nodePositions[j].z;
            }
        }
    }

    lineSegmentsMesh.geometry.setDrawRange(0, lineIdx / 3);
    lineSegmentsMesh.geometry.attributes.position.needsUpdate = true;
}

// Animation Loop
const clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);

    const elapsedTime = clock.getElapsedTime();

    // Rotate Constellation Sphere
    if (constellationNodes) {
        constellationNodes.rotation.y = elapsedTime * 0.12;
    }
    if (lineSegmentsMesh) {
        lineSegmentsMesh.rotation.y = elapsedTime * 0.12;
    }
    if (outerDust) {
        outerDust.rotation.y = elapsedTime * 0.05;
    }

    // Animate Constellation Node Connections
    updateConstellation(elapsedTime);

    // Pulse Horizontal Lens Flare Beam
    if (flareBeamMesh) {
        const pulse = 0.55 + Math.sin(elapsedTime * 4) * 0.1;
        flareBeamMesh.material.opacity = pulse;
    }

    // Draw Right Side Audio Visualizer
    drawRightAudioWave(elapsedTime);

    renderer.render(scene, camera);
}

// Right Side Vertical Bar Audio Visualizer
function drawRightAudioWave(time) {
    if (!rightCtx) return;
    const w = rightCanvas.width;
    const h = rightCanvas.height;

    rightCtx.clearRect(0, 0, w, h);

    const numBars = 24;
    const barWidth = 4;
    const gap = 3;
    const totalW = numBars * (barWidth + gap);
    const startX = w - totalW;

    for (let i = 0; i < numBars; i++) {
        const factor = Math.sin(time * 6 + i * 0.3) * 0.4 + 0.5;
        const barHeight = factor * h * (micActive ? 0.9 : 0.4);

        rightCtx.fillStyle = micActive ? '#00ff88' : '#ff7700';
        rightCtx.shadowColor = micActive ? '#00ff88' : '#ff7700';
        rightCtx.shadowBlur = 6;

        rightCtx.fillRect(startX + i * (barWidth + gap), (h - barHeight) / 2, barWidth, barHeight);
    }
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

let livekitRoom = null;
let currentUIState = "IDLE";

function updateUIState(state, detailText) {
    currentUIState = state;
    console.log(`[FRIDAY] State -> ${state} (${detailText || ''})`);

    const triggerLabel = document.getElementById('trigger-label');
    const listeningLbl = document.getElementById('listening-lbl');
    const micBtn = document.getElementById('btn-mic');

    if (triggerLabel) {
        triggerLabel.innerText = state === "IDLE" ? "TAP TO SPEAK" : state;
    }
    if (listeningLbl) {
        listeningLbl.innerText = detailText || (state === "SPEAKING" ? "FRIDAY SPEAKING" : "I'M LISTENING");
    }
    if (micBtn) {
        if (["CONNECTED", "LISTENING", "SPEAKING"].includes(state)) {
            micBtn.classList.add('active');
        } else {
            micBtn.classList.remove('active');
        }
    }
}

async function connectLiveKit() {
    updateUIState("CONNECTING", "FETCHING TOKEN");
    try {
        const tokenRes = await fetch("http://127.0.0.1:8000/api/token?room=friday-room&identity=user-browser");
        if (!tokenRes.ok) {
            throw new Error(`Token endpoint HTTP ${tokenRes.status}`);
        }
        const data = await tokenRes.json();
        if (data.error) {
            throw new Error(data.error);
        }

        console.log("[FRIDAY] LiveKit token received securely");

        const room = new window.LiveKit.Room({
            adaptiveStream: true,
            dynacast: true
        });

        room.on(window.LiveKit.RoomEvent.TrackSubscribed, (track, publication, participant) => {
            console.log("[FRIDAY] Agent audio track subscribed:", track.kind);
            if (track.kind === "audio") {
                const audioElement = document.getElementById("remote-audio");
                if (audioElement) {
                    track.attach(audioElement);
                    console.log("[FRIDAY] Audio track attached to speaker");
                }
                updateUIState("SPEAKING", "FRIDAY SPEAKING");
            }
        });

        room.on(window.LiveKit.RoomEvent.TrackUnsubscribed, (track) => {
            if (track.kind === "audio") {
                track.detach();
                updateUIState("IDLE", "TAP TO SPEAK");
            }
        });

        room.on(window.LiveKit.RoomEvent.ActiveSpeakersChanged, (speakers) => {
            const agentSpeaking = speakers.some(s => s.identity !== "user-browser");
            if (agentSpeaking) {
                updateUIState("SPEAKING", "FRIDAY SPEAKING");
            } else if (micActive) {
                updateUIState("LISTENING", "LISTENING LIVE");
            }
        });

        room.on(window.LiveKit.RoomEvent.Disconnected, () => {
            console.log("[FRIDAY] Disconnected from room");
            updateUIState("IDLE", "TAP TO SPEAK");
            micActive = false;
            livekitRoom = null;
        });

        await room.connect(data.url, data.token);
        console.log("[FRIDAY] Connected to LiveKit room:", data.room);
        updateUIState("CONNECTED", "ROOM CONNECTED");

        await room.localParticipant.setMicrophoneEnabled(true);
        console.log("[FRIDAY] Local microphone published");
        updateUIState("LISTENING", "LISTENING LIVE");

        livekitRoom = room;
        micActive = true;

    } catch (err) {
        console.error("[FRIDAY] LiveKit connection error:", err);
        updateUIState("ERROR", err.message || "CONNECTION FAILED");
        micActive = false;
    }
}

async function disconnectLiveKit() {
    if (livekitRoom) {
        await livekitRoom.disconnect();
        livekitRoom = null;
    }
    micActive = false;
    updateUIState("IDLE", "TAP TO SPEAK");
}

// Mic Button Setup
function setupMicButton() {
    const btn = document.getElementById('btn-mic');
    if (!btn) return;

    btn.addEventListener('click', async () => {
        if (!micActive && (!livekitRoom || livekitRoom.state !== "connected")) {
            await connectLiveKit();
        } else {
            await disconnectLiveKit();
        }
    });
}

// DOM Init
document.addEventListener('DOMContentLoaded', () => {
    updateClock();
    setInterval(updateClock, 1000);
    initScene();
    animate();
    setupMicButton();
});

