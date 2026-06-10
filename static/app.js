"use strict";

/* ==========================================
   Toast System
========================================== */

function showToast(message, type = "success") {

    let container =
        document.getElementById(
            "toastContainer"
        );

    if (!container) {

        container =
            document.createElement("div");

        container.id =
            "toastContainer";

        container.style.position =
            "fixed";

        container.style.top =
            "20px";

        container.style.right =
            "20px";

        container.style.zIndex =
            "9999";

        document.body.appendChild(
            container
        );
    }

    const toast =
        document.createElement("div");

    toast.className =
        `alert alert-${type}`;

    toast.style.minWidth =
        "250px";

    toast.style.marginBottom =
        "10px";

    toast.style.boxShadow =
        "0 10px 30px rgba(0,0,0,.1)";

    toast.innerHTML = message;

    container.appendChild(
        toast
    );

    setTimeout(() => {

        toast.style.opacity = "0";

        toast.style.transition =
            "0.3s";

        setTimeout(
            () => toast.remove(),
            300
        );

    }, 2500);
}

/* ==========================================
   Sidebar Toggle
========================================== */

function initializeSidebar() {

    const toggle =
        document.getElementById(
            "sidebarToggle"
        );

    const sidebar =
        document.getElementById(
            "sidebar"
        );

    if (
        !toggle ||
        !sidebar
    ) {
        return;
    }

    toggle.addEventListener(
        "click",
        () => {

            sidebar.classList.toggle(
                "show"
            );

        }
    );
}

initializeSidebar();

/* ==========================================
   Copy To Clipboard
========================================== */

async function copyToClipboard(text) {

    try {

        await navigator.clipboard.writeText(
            text
        );

        showToast(
            "Copied to clipboard"
        );

    } catch (error) {

        console.error(error);

        showToast(
            "Copy failed",
            "danger"
        );
    }
}

document.addEventListener(
    "click",
    function (event) {

        const button =
            event.target.closest(
                "[data-copy]"
            );

        if (!button) {
            return;
        }

        const value =
            button.getAttribute(
                "data-copy"
            );

        if (!value) {
            return;
        }

        copyToClipboard(
            value
        );
    }
);

/* ==========================================
   Confirm Dialog
========================================== */

document.addEventListener(
    "click",
    function (event) {

        const button =
            event.target.closest(
                "[data-confirm]"
            );

        if (!button) {
            return;
        }

        const message =
            button.getAttribute(
                "data-confirm"
            ) ||
            "Are you sure?";

        if (
            !window.confirm(
                message
            )
        ) {
            event.preventDefault();
        }
    }
);

/* ==========================================
   Search Filter
========================================== */

function initializeFilters() {

    const search =
        document.getElementById(
            "tableSearch"
        );

    if (!search) {
        return;
    }

    search.addEventListener(
        "input",
        function () {

            const value =
                this.value
                    .toLowerCase()
                    .trim();

            document
                .querySelectorAll(
                    "[data-filter-row]"
                )
                .forEach(row => {

                    const text =
                        row.innerText
                            .toLowerCase();

                    row.style.display =
                        text.includes(
                            value
                        )
                            ? ""
                            : "none";
                });
        }
    );
}

initializeFilters();

/* ==========================================
   Subscription Refresh
========================================== */

async function refreshSubscription(id) {

    try {

        showToast(
            "Refreshing subscription...",
            "primary"
        );

        const response =
            await fetch(
                `/subscriptions/${id}/refresh`,
                {
                    method: "POST"
                }
            );

        if (!response.ok) {

            throw new Error(
                "Refresh failed"
            );
        }

        showToast(
            "Refresh completed"
        );

        setTimeout(
            () =>
                window.location.reload(),
            800
        );

    } catch (error) {

        console.error(error);

        showToast(
            "Refresh failed",
            "danger"
        );
    }
}

/* ==========================================
   Auto Refresh
========================================== */

function autoRefresh() {

    const interval =
        document.body.dataset
            .refresh;

    if (!interval) {
        return;
    }

    const seconds =
        parseInt(interval);

    if (
        Number.isNaN(seconds) ||
        seconds <= 0
    ) {
        return;
    }

    setTimeout(
        () =>
            window.location.reload(),
        seconds * 1000
    );
}

autoRefresh();

/* ==========================================
   Loading Buttons
========================================== */

document.addEventListener(
    "submit",
    function (event) {

        const form =
            event.target;

        if (
            !(
                form instanceof
                HTMLFormElement
            )
        ) {
            return;
        }

        const button =
            form.querySelector(
                "button[type='submit']"
            );

        if (!button) {
            return;
        }

        const original =
            button.innerHTML;

        button.disabled = true;

        button.innerHTML =
            `
            <span class="spinner-border spinner-border-sm me-2"></span>
            Processing...
        `;

        setTimeout(
            () => {

                button.disabled =
                    false;

                button.innerHTML =
                    original;

            },
            10000
        );
    }
);

/* ==========================================
   Active Menu Highlight
========================================== */

function initializeActiveMenu() {

    const current =
        window.location.pathname;

    document
        .querySelectorAll(
            ".sidebar-link"
        )
        .forEach(link => {

            const href =
                link.getAttribute(
                    "href"
                );

            if (
                href &&
                current.startsWith(
                    href
                )
            ) {

                link.style.background =
                    "var(--sidebar-active)";

                link.style.color =
                    "#fff";
            }
        });
}


/* ==========================================
   Subscription Edit Modal
========================================== */

function openEditModal(data) {

    const modal =
        document.getElementById(
            "editSubscriptionModal"
        );

    if (!modal) {
        return;
    }

    document.getElementById(
        "editSubscriptionId"
    ).value = data.id;

    document.getElementById(
        "editSubscriptionName"
    ).value = data.name || "";

    document.getElementById(
        "editRemarkName"
    ).value = data.remark || "";

    document.getElementById(
        "editMessageLimit"
    ).value = data.limit || 300;

    document.getElementById(
        "editEncoding"
    ).value =
        data.base64
            ? "1"
            : "0";

    const channelSelect =
        document.getElementById(
            "editChannels"
        );

    if (channelSelect) {

        Array.from(
            channelSelect.options
        ).forEach(option => {

            option.selected =
                data.channels.indexOf(
                    parseInt(option.value)
                ) !== -1

        });
    }

    const form =
        document.getElementById(
            "editSubscriptionForm"
        );

    form.action =
        `/subscriptions/${data.id}/edit`;

    const bootstrapModal =
        new bootstrap.Modal(
            modal
        );

    bootstrapModal.show();
}

initializeActiveMenu();