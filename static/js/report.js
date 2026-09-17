/**
 * HIMA-LENS: Field Telemetry & Landslide Incident Reporting
 * Dedicated client-side module for GPS lock, map pin-drop, photo upload, and instant community feed.
 */

document.addEventListener("DOMContentLoaded", function () {
    let map = null;
    let marker = null;
    let selectedPhotoFile = null;

    // Default center: Himachal Pradesh
    const DEFAULT_LAT = 31.708;
    const DEFAULT_LNG = 76.932;

    const latInput = document.getElementById("rep-lat");
    const lngInput = document.getElementById("rep-lng");
    const gpsBtn = document.getElementById("report-gps-btn");
    const gpsFeedback = document.getElementById("report-gps-feedback");
    const photoFileInput = document.getElementById("rep-photo-file");
    const dropzoneArea = document.getElementById("dropzone-area");
    const dropzoneEmpty = document.getElementById("dropzone-empty");
    const dropzonePreview = document.getElementById("dropzone-preview");
    const previewImg = document.getElementById("preview-img-element");
    const previewFilename = document.getElementById("preview-filename");
    const btnRemovePhoto = document.getElementById("btn-remove-photo");
    const dateInput = document.getElementById("rep-date");
    const reportForm = document.getElementById("citizen-report-form");
    const statusBanner = document.getElementById("report-status-banner");
    const submitBtn = document.getElementById("btn-submit-report");
    const recentFeedContainer = document.getElementById("recent-reports-grid");

    // Initialize Default Datetime
    if (dateInput) {
        const now = new Date();
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        dateInput.value = now.toISOString().slice(0, 16);
    }

    // 1. Initialize Interactive Mini Map
    function initMap() {
        const mapContainer = document.getElementById("report-map");
        if (!mapContainer || typeof L === "undefined") return;

        map = L.map("report-map", {
            zoomControl: true,
            scrollWheelZoom: false
        }).setView([DEFAULT_LAT, DEFAULT_LNG], 8);

        L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
            maxZoom: 18,
            attribution: '&copy; <a href="https://carto.com/">CARTO</a>'
        }).addTo(map);

        // Custom Marker Icon matching Swiss editorial theme
        const pinIcon = L.divIcon({
            className: "report-pin-marker",
            html: '<div class="report-pin-symbol"><span>📍</span></div>',
            iconSize: [34, 34],
            iconAnchor: [17, 34],
            popupAnchor: [0, -34]
        });

        marker = L.marker([DEFAULT_LAT, DEFAULT_LNG], {
            icon: pinIcon,
            draggable: true
        }).addTo(map);

        // Update inputs on marker drag
        marker.on("dragend", function (e) {
            const pos = marker.getLatLng();
            updateCoordinates(pos.lat, pos.lng);
        });

        // Drop marker on map click
        map.on("click", function (e) {
            marker.setLatLng(e.latlng);
            updateCoordinates(e.latlng.lat, e.latlng.lng);
        });

        // Set initial coordinates
        updateCoordinates(DEFAULT_LAT, DEFAULT_LNG);
    }

    function updateCoordinates(lat, lng) {
        if (latInput) latInput.value = Number(lat).toFixed(6);
        if (lngInput) lngInput.value = Number(lng).toFixed(6);
    }

    // Update marker if coordinates are typed manually
    function onManualCoordChange() {
        const lat = parseFloat(latInput?.value);
        const lng = parseFloat(lngInput?.value);
        if (!isNaN(lat) && !isNaN(lng) && lat >= 30 && lat <= 34 && lng >= 75 && lng <= 80) {
            if (marker && map) {
                marker.setLatLng([lat, lng]);
                map.panTo([lat, lng]);
            }
        }
    }

    if (latInput) latInput.addEventListener("input", onManualCoordChange);
    if (lngInput) lngInput.addEventListener("input", onManualCoordChange);

    // 2. High-Precision GPS Lock
    if (gpsBtn) {
        gpsBtn.addEventListener("click", function () {
            if (!navigator.geolocation) {
                if (gpsFeedback) gpsFeedback.textContent = "GPS not supported by your browser";
                return;
            }

            if (gpsFeedback) {
                gpsFeedback.textContent = "Acquiring satellite lock...";
                gpsFeedback.className = "gps-feedback active";
            }
            gpsBtn.disabled = true;

            navigator.geolocation.getCurrentPosition(
                function (position) {
                    gpsBtn.disabled = false;
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    const acc = Math.round(position.coords.accuracy);

                    // Check bounds for Himachal Pradesh
                    if (lat < 30.0 || lat > 34.0 || lng < 75.0 || lng > 80.0) {
                        if (gpsFeedback) {
                            gpsFeedback.textContent = `Location (${lat.toFixed(2)}°N, ${lng.toFixed(2)}°E) is outside Himachal Pradesh`;
                            gpsFeedback.className = "gps-feedback warning";
                        }
                    } else {
                        if (gpsFeedback) {
                            gpsFeedback.textContent = `Locked: ±${acc}m accuracy`;
                            gpsFeedback.className = "gps-feedback success";
                        }
                    }

                    updateCoordinates(lat, lng);
                    if (marker && map) {
                        marker.setLatLng([lat, lng]);
                        map.setView([lat, lng], 13);
                    }
                },
                function (error) {
                    gpsBtn.disabled = false;
                    if (gpsFeedback) {
                        let msg = "Could not retrieve GPS coordinates";
                        if (error.code === error.PERMISSION_DENIED) {
                            msg = "Location permission denied";
                        } else if (error.code === error.POSITION_UNAVAILABLE) {
                            msg = "Location signal unavailable";
                        } else if (error.code === error.TIMEOUT) {
                            msg = "GPS request timed out";
                        }
                        gpsFeedback.textContent = msg;
                        gpsFeedback.className = "gps-feedback warning";
                    }
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                }
            );
        });
    }

    // 3. Photo Dropzone & Live Camera Capture
    if (dropzoneArea && photoFileInput) {
        dropzoneArea.addEventListener("click", function (e) {
            if (e.target !== btnRemovePhoto) {
                photoFileInput.click();
            }
        });

        dropzoneArea.addEventListener("dragover", function (e) {
            e.preventDefault();
            dropzoneArea.classList.add("dragover");
        });

        dropzoneArea.addEventListener("dragleave", function () {
            dropzoneArea.classList.remove("dragover");
        });

        dropzoneArea.addEventListener("drop", function (e) {
            e.preventDefault();
            dropzoneArea.classList.remove("dragover");
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handlePhotoSelection(e.dataTransfer.files[0]);
            }
        });

        photoFileInput.addEventListener("change", function () {
            if (photoFileInput.files && photoFileInput.files[0]) {
                handlePhotoSelection(photoFileInput.files[0]);
            }
        });
    }

    function handlePhotoSelection(file) {
        if (!file.type.startsWith("image/")) {
            alert("Please select a valid image file (JPG, PNG, WebP).");
            return;
        }

        selectedPhotoFile = file;
        const reader = new FileReader();
        reader.onload = function (e) {
            if (previewImg) previewImg.src = e.target.result;
            if (previewFilename) previewFilename.textContent = `${file.name} (${(file.size / 1024).toFixed(0)} KB)`;
            if (dropzoneEmpty) dropzoneEmpty.style.display = "none";
            if (dropzonePreview) dropzonePreview.style.display = "block";
        };
        reader.readAsDataURL(file);
    }

    if (btnRemovePhoto) {
        btnRemovePhoto.addEventListener("click", function (e) {
            e.stopPropagation();
            clearPhotoSelection();
        });
    }

    function clearPhotoSelection() {
        selectedPhotoFile = null;
        if (photoFileInput) photoFileInput.value = "";
        if (previewImg) previewImg.src = "";
        if (dropzoneEmpty) dropzoneEmpty.style.display = "flex";
        if (dropzonePreview) dropzonePreview.style.display = "none";
    }

    // 4. Form Submission
    if (reportForm) {
        reportForm.addEventListener("submit", async function (e) {
            e.preventDefault();

            const lat = parseFloat(latInput?.value);
            const lng = parseFloat(lngInput?.value);

            if (isNaN(lat) || isNaN(lng)) {
                showStatus("Please specify valid latitude and longitude coordinates.", "error");
                return;
            }

            if (lat < 30.0 || lat > 34.0 || lng < 75.0 || lng > 80.0) {
                showStatus("Report coordinates must be within Himachal Pradesh (30°N–34°N, 75°E–80°E).", "error");
                return;
            }

            const formData = new FormData(reportForm);
            if (selectedPhotoFile) {
                formData.set("photo", selectedPhotoFile);
            }

            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = "<span>Submitting Field Report...</span>";
            }

            try {
                const response = await fetch("/api/reports", {
                    method: "POST",
                    body: formData
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    const reportId = data.report?.id || "HL-CR-SUBMITTED";
                    showStatus(
                        `<strong>Field Report Registered!</strong> Incident Record ID: <code>${reportId}</code>. Your submission has been pinned to the spatial inventory. <a href="/explore" class="status-action-link">Open in Spatial Explorer &nearr;</a>`,
                        "success"
                    );

                    // Reset fields except district
                    reportForm.reset();
                    clearPhotoSelection();
                    if (dateInput) {
                        const now = new Date();
                        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
                        dateInput.value = now.toISOString().slice(0, 16);
                    }
                    updateCoordinates(DEFAULT_LAT, DEFAULT_LNG);
                    if (marker && map) {
                        marker.setLatLng([DEFAULT_LAT, DEFAULT_LNG]);
                    }

                    // Reload recent feed
                    loadRecentReports();
                } else {
                    showStatus(data.message || "Failed to submit field report. Please check required fields.", "error");
                }
            } catch (err) {
                console.error("Report submission failed:", err);
                showStatus("Network or server error while transmitting report. Please try again.", "error");
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<span>Submit Field Report</span> <span class="submit-arrow">&rarr;</span>';
                }
            }
        });
    }

    function showStatus(html, type) {
        if (!statusBanner) return;
        statusBanner.innerHTML = html;
        statusBanner.className = `report-status-banner ${type}`;
        statusBanner.style.display = "block";
        statusBanner.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    // 5. Load Recent Field Reports
    async function loadRecentReports() {
        if (!recentFeedContainer) return;

        try {
            const res = await fetch("/api/reports");
            if (!res.ok) return;
            const data = await res.json();
            const features = data.features || [];

            if (features.length === 0) {
                recentFeedContainer.innerHTML = `
                    <div class="empty-feed-card">
                        <span class="empty-icon">🏔️</span>
                        <h3>No Community Reports Filed Yet</h3>
                        <p>Be the first field observer to document a slope failure in Himachal Pradesh using the form above.</p>
                    </div>
                `;
                return;
            }

            // Render cards in reverse chronological order
            recentFeedContainer.innerHTML = "";
            const sorted = [...features].reverse().slice(0, 6);

            sorted.forEach(feature => {
                const p = feature.properties || {};
                const coords = feature.geometry?.coordinates || [0, 0];
                const card = document.createElement("article");
                card.className = "recent-report-card";

                const photoHtml = p.photo_url
                    ? `<div class="recent-card-media"><img src="${p.photo_url}" alt="Observation thumbnail" loading="lazy"></div>`
                    : `<div class="recent-card-media placeholder"><span class="media-icon">📍</span></div>`;

                const severityClass = `severity-${(p.severity || "moderate").toLowerCase()}`;

                card.innerHTML = `
                    ${photoHtml}
                    <div class="recent-card-body">
                        <div class="recent-card-meta">
                            <span class="recent-district-badge">${escapeHtml(p.district || "Himachal Pradesh")}</span>
                            <span class="recent-severity-badge ${severityClass}">${escapeHtml(p.severity || "Moderate")}</span>
                        </div>
                        <h3 class="recent-card-title">${escapeHtml(p.movement_type || "Landslide")} Incident</h3>
                        <p class="recent-card-desc">${escapeHtml(p.description || "Field observation recorded.")}</p>
                        <div class="recent-card-footer">
                            <span class="recent-coords">${coords[1].toFixed(4)}°N, ${coords[0].toFixed(4)}°E</span>
                            <span class="recent-id">${escapeHtml(p.id || "")}</span>
                        </div>
                    </div>
                `;

                // Interactive Click Handler: Open Detailed Incident Modal
                card.addEventListener("click", () => {
                    openReportDetail(p, coords);
                });

                recentFeedContainer.appendChild(card);
            });
        } catch (e) {
            console.error("Failed to load recent reports:", e);
        }
    }

    function openReportDetail(p, coords) {
        const modal = document.getElementById("report-detail-modal");
        if (!modal) return;

        const detailId = document.getElementById("detail-id");
        if (detailId) detailId.textContent = p.id || "HL-CR-OBSERVATION";

        const detailTitle = document.getElementById("report-detail-title");
        if (detailTitle) detailTitle.textContent = `${p.movement_type || "Landslide"} — ${p.district || "Himachal Pradesh"}`;

        const detailDistrict = document.getElementById("detail-district");
        if (detailDistrict) detailDistrict.textContent = p.district || "Himachal Pradesh";

        const detailSeverity = document.getElementById("detail-severity");
        if (detailSeverity) {
            detailSeverity.textContent = (p.severity || "Moderate").toUpperCase();
            detailSeverity.className = `meta-val severity-${(p.severity || "moderate").toLowerCase()}`;
        }

        const detailMovement = document.getElementById("detail-movement");
        if (detailMovement) detailMovement.textContent = p.movement_type || "Slide";

        const detailDate = document.getElementById("detail-date");
        if (detailDate) detailDate.textContent = p.incident_date || "Recent Observation";

        const detailCoords = document.getElementById("detail-coords");
        if (detailCoords) detailCoords.textContent = `${coords[1].toFixed(5)}° N, ${coords[0].toFixed(5)}° E`;

        const detailDescription = document.getElementById("detail-description");
        if (detailDescription) detailDescription.textContent = p.description || "No additional field notes provided.";

        const detailReporter = document.getElementById("detail-reporter");
        if (detailReporter) {
            const name = p.reporter_name ? p.reporter_name : "Anonymous Observer";
            const contact = p.contact_info ? ` (${p.contact_info})` : "";
            detailReporter.textContent = `${name}${contact}`;
        }

        const photoImg = document.getElementById("detail-photo");
        const mediaWrap = document.getElementById("detail-media-wrap");
        if (p.photo_url && photoImg && mediaWrap) {
            photoImg.src = p.photo_url;
            mediaWrap.style.display = "block";
        } else if (mediaWrap) {
            mediaWrap.style.display = "none";
        }

        const pinMapBtn = document.getElementById("btn-detail-pin-map");
        if (pinMapBtn) {
            pinMapBtn.onclick = () => {
                modal.setAttribute("hidden", "");
                if (marker && map) {
                    marker.setLatLng([coords[1], coords[0]]);
                    map.setView([coords[1], coords[0]], 12);
                    updateCoordinates(coords[1], coords[0]);
                    document.getElementById("report-map")?.scrollIntoView({ behavior: "smooth", block: "center" });
                }
            };
        }

        modal.removeAttribute("hidden");
    }

    const closeDetailBtn = document.getElementById("btn-close-detail");
    closeDetailBtn?.addEventListener("click", () => {
        document.getElementById("report-detail-modal")?.setAttribute("hidden", "");
    });

    document.getElementById("report-detail-modal")?.addEventListener("click", (e) => {
        if (e.target === document.getElementById("report-detail-modal")) {
            document.getElementById("report-detail-modal")?.setAttribute("hidden", "");
        }
    });

    function escapeHtml(str) {
        return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
    }

    // Initialize Map and Feed
    initMap();
    loadRecentReports();
});
