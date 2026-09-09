// =============================================================================
// static/app.js
// =============================================================================

// ── Toast auto-show ───────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.toast').forEach(el => {
    new bootstrap.Toast(el, { delay: 6000 }).show();
  });
});


// ── Tooltip initialisation ────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
    new bootstrap.Tooltip(el);
  });
});


// ── Inline fetch modal loader ─────────────────────────────────────────────────
// Usage: <button data-url="/partial-url" data-bs-toggle="modal"
//               data-bs-target="#Modal">
document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('Modal');
  if (!modal) return;

  modal.addEventListener('show.bs.modal', e => {
    const trigger = e.relatedTarget;
    const url = trigger && trigger.dataset.url;
    if (!url) return;

    const content = modal.querySelector('.modal-content');
    content.innerHTML = '<div class="text-center p-4"><div class="spinner-border text-primary"></div></div>';

    fetch(url)
      .then(r => r.text())
      .then(html => { content.innerHTML = html; })
      .catch(() => { content.innerHTML = '<div class="alert alert-danger m-3">Failed to load content.</div>'; });
  });
});

// ── Auto-dismiss alerts ───────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert-dismissible').forEach(el => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      if (bsAlert) bsAlert.close();
    }, 8000);
  });
});

// ── Download button spinner ───────────────────────────────────────────────────
function handleDownload(btn) {
  btn.classList.add('loading');
  setTimeout(() => btn.classList.remove('loading'), 2000);
}


// ── Static Notification ───────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
  const notifBell = document.getElementById("notifBell");
  const list = document.getElementById("notifList");
  const badge = document.getElementById("notifBadge");
  const empty = document.getElementById("notifEmpty");
  const modalContainer = document.getElementById("notifModalContainer");

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  function render(data) {
    // Remove previous items
    list.querySelectorAll(".notif-item").forEach(el => el.remove());

    const hasItems = data.notifications && data.notifications.length > 0;
    empty.classList.toggle("d-none", hasItems);

    // Update badge
    if (data.unread_count > 0) {
      badge.textContent = data.unread_count > 99 ? "99+" : data.unread_count;
      badge.classList.remove("d-none");
    } else {
      badge.classList.add("d-none");
    }

    data.notifications.forEach(n => {
      const li = document.createElement("li");
      li.className = "notif-item";
      li.innerHTML = `
        <a href="#"
           class="dropdown-item d-flex flex-column py-2 ${n.is_read ? "" : "fw-semibold bg-light"}"
           data-id="${n.id}">
          <span>${escapeHtml(n.title)}</span>
          <small class="text-muted text-truncate" style="max-width: 280px;">${escapeHtml(n.message)}</small>
        </a>`;
      list.appendChild(li);
    });
  }

  function loadNotifications() {
    fetch("/notifications/api/recent?limit=5")
      .then(res => {
        if (!res.ok) throw new Error("Failed to fetch recent");
        return res.json();
      })
      .then(render)
      .catch(err => console.error("Notifications load error:", err));
  }

  // Click a notification: open modal + mark read in background
  list.addEventListener("click", (e) => {
    const link = e.target.closest("a[data-id]");
    if (!link) return;
    e.preventDefault();

    const id = link.dataset.id;

    // Close Bootstrap dropdown
    const bsDropdown = bootstrap.Dropdown.getInstance(notifBell);
    if (bsDropdown) bsDropdown.hide();

    // 1. Mark as read in background
    fetch(`/notifications/api/${id}/read`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken || "",
      },
    })
      .then(r => r.json())
      .then(() => loadNotifications()) // refresh badge
      .catch(err => console.error("Mark read failed:", err));

    // 2. Fetch and show detail modal
    fetch(`/notifications/${id}/modal`)
      .then(res => {
        if (!res.ok) throw new Error("Failed to load details");
        return res.text();
      })
      .then(html => {
        modalContainer.innerHTML = html;
        const modalEl = modalContainer.querySelector(".modal");
        if (!modalEl) return;

        const bsModal = new bootstrap.Modal(modalEl);
        bsModal.show();

        // Clean up modal from DOM after it closes
        modalEl.addEventListener("hidden.bs.modal", () => {
          modalContainer.innerHTML = "";
        });
      })
      .catch(err => console.error("Modal load error:", err));
  });

  // Initial load + polling
  loadNotifications();
  setInterval(loadNotifications, 30000);
});