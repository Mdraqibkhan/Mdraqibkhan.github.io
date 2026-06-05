// Auto-Update Google Scholar Data
// Replace the existing loadScholarData IIFE in your HTML with this version.
// It handles the richer scholar.json produced by scrape_scholar.py,
// including per-paper direct links and an "updated" timestamp badge.

(function loadScholarData() {
  fetch('scholar.json?v=' + Date.now())
    .then(res => res.ok ? res.json() : Promise.reject('No scholar.json'))
    .then(data => {

      // --- Top-level stats ---
      const statMap = { citations: 'citations', publications: 'publications', h_index: 'h_index' };
      Object.entries(statMap).forEach(([key, stat]) => {
        if (data[key] === undefined) return;
        const el = document.querySelector(`[data-stat="${stat}"]`);
        if (!el) return;
        el.setAttribute('data-target', data[key]);
        el.innerText = data[key];
      });

      // --- Per-paper citation badges + direct links ---
      if (data.papers && Array.isArray(data.papers)) {
        const badges = document.querySelectorAll('.dynamic-citation');
        const linkBtns = document.querySelectorAll('#pub-list .flex-shrink-0');

        data.papers.forEach((paper, idx) => {
          // Update citation badge
          if (badges[idx] && paper.citations !== undefined) {
            const c = paper.citations;
            badges[idx].innerText = c === 1 ? '1 citation' : c > 0 ? `${c} citations` : '–';
          }
          // Update external link to point directly to the paper
          if (linkBtns[idx] && paper.scholar_url) {
            linkBtns[idx].href = paper.scholar_url;
            linkBtns[idx].setAttribute('aria-label', `View "${paper.title}" on Google Scholar`);
          }
        });
      }

      // --- "Last updated" badge in the footer note ---
      if (data.updated_at) {
        const badge = document.getElementById('scholar-updated');
        if (badge) {
          const d = new Date(data.updated_at);
          badge.innerText = 'Last synced: ' + d.toLocaleDateString('en-IE', {
            day: 'numeric', month: 'short', year: 'numeric'
          });
        }
      }
    })
    .catch(err => console.log('Scholar auto-update:', err));
})();
