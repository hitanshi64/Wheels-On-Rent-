/**
 * Nearest Branch Locator
 * - Tries browser Geolocation API first.
 * - If denied/unavailable, shows a manual "choose your city" modal.
 * - Caches the result in localStorage so we don't ask again every page load.
 * - Renders the result into the #branch-widget-bar included on every page (base.html).
 */
(function () {
  const NEAREST_BRANCH_URL = window.WOR_NEAREST_BRANCH_URL;
  const BRANCH_CITIES_URL = window.WOR_BRANCH_CITIES_URL;

  const bar = document.getElementById('branch-widget-bar');
  const textEl = document.getElementById('branch-widget-text');
  const directionsBtn = document.getElementById('branch-directions-btn');
  const citySelect = document.getElementById('manual-city-select');
  const cityConfirmBtn = document.getElementById('manual-city-confirm');

  if (!bar) return;

  function showBar() {
    bar.style.display = 'block';
  }

  function renderBranch(data) {
    const mapIframe = document.getElementById('branch-map-iframe');
    const mapFallback = document.getElementById('contact-branch-map-fallback');

    if (!data.found) {
      textEl.innerHTML = `<span class="branch-widget-muted">${data.message || 'No branches available yet.'}</span>`;
      directionsBtn.style.display = 'none';
      showBar();
      if (mapFallback) mapFallback.textContent = data.message || 'No branches available yet.';
      return;
    }

    const distanceText = (data.distance_km !== null && data.distance_km !== undefined)
      ? ` &bull; <span class="branch-widget-muted">${data.distance_km} km away</span>`
      : '';

    textEl.innerHTML =
      `Your nearest branch: <strong>${data.name}</strong>, ${data.city}` +
      `${distanceText}<br><span class="branch-widget-muted">${data.address} &bull; ${data.contact_number}</span>`;

    directionsBtn.href = data.directions_url;
    directionsBtn.style.display = 'inline-block';
    showBar();

    if (mapIframe) {
      mapIframe.src = data.map_embed_url;
    }
    if (mapFallback) {
      mapFallback.innerHTML =
        `<strong>${data.name}</strong> &bull; ${data.address} &bull; ${data.contact_number}` +
        `${distanceText ? distanceText : ''}` +
        ` &bull; <a href="${data.directions_url}" target="_blank">Get Directions</a>`;
    }

    localStorage.setItem('wor_nearest_branch_cache', JSON.stringify({ data: data, ts: Date.now() }));
  }

  function fetchNearestByCoords(lat, lon) {
    fetch(`${NEAREST_BRANCH_URL}?lat=${lat}&lon=${lon}`)
      .then((res) => res.json())
      .then(renderBranch)
      .catch(() => {
        textEl.textContent = 'Could not load branch info right now.';
        showBar();
      });
  }

  function fetchNearestByCity(city) {
    fetch(`${NEAREST_BRANCH_URL}?city=${encodeURIComponent(city)}`)
      .then((res) => res.json())
      .then(renderBranch)
      .catch(() => {
        textEl.textContent = 'Could not load branch info right now.';
        showBar();
      });
  }

  function openCityModalWithOptions() {
    fetch(BRANCH_CITIES_URL)
      .then((res) => res.json())
      .then((data) => {
        citySelect.innerHTML = '';
        (data.cities || []).forEach((c) => {
          const opt = document.createElement('option');
          opt.value = c;
          opt.textContent = c;
          citySelect.appendChild(opt);
        });
      });

    const modalEl = document.getElementById('chooseCityModal');
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
  }

  cityConfirmBtn.addEventListener('click', function () {
    const city = citySelect.value;
    if (!city) return;
    localStorage.setItem('wor_manual_city', city);
    localStorage.removeItem('wor_nearest_branch_cache');
    fetchNearestByCity(city);
    const modalEl = document.getElementById('chooseCityModal');
    bootstrap.Modal.getInstance(modalEl).hide();
  });

  // Allow "Change City" to always reopen the picker, regardless of geolocation state
  document.querySelectorAll('[data-bs-target="#chooseCityModal"]').forEach((btn) => {
    btn.addEventListener('click', openCityModalWithOptions);
  });

  function init() {
    // 1) Use cached result if it's recent (within 1 hour) to avoid refetching every page
    const cachedRaw = localStorage.getItem('wor_nearest_branch_cache');
    if (cachedRaw) {
      try {
        const cached = JSON.parse(cachedRaw);
        if (Date.now() - cached.ts < 60 * 60 * 1000) {
          renderBranch(cached.data);
          return;
        }
      } catch (e) { /* ignore corrupt cache */ }
    }

    // 2) A manually chosen city takes priority over asking again
    const manualCity = localStorage.getItem('wor_manual_city');
    if (manualCity) {
      fetchNearestByCity(manualCity);
      return;
    }

    // 3) Try browser Geolocation API
    if (navigator.geolocation) {
      textEl.textContent = 'Finding your nearest branch…';
      showBar();
      navigator.geolocation.getCurrentPosition(
        function (position) {
          fetchNearestByCoords(position.coords.latitude, position.coords.longitude);
        },
        function () {
          // Permission denied or unavailable -> ask the user to pick a city manually
          textEl.innerHTML = '<span class="branch-widget-muted">Location access denied. Please choose your city.</span>';
          showBar();
          openCityModalWithOptions();
        },
        { timeout: 8000 }
      );
    } else {
      openCityModalWithOptions();
    }
  }

  document.addEventListener('DOMContentLoaded', init);
})();
