"use strict";

/* ==========================================
   Toast / Notifications
========================================== */

function showMessage(message) {
    console.log(message);
}

/* ==========================================
   Copy To Clipboard
========================================== */

async function copyToClipboard(text) {

    try {

        await navigator.clipboard.writeText(text);

        showMessage("Copied");

    } catch (error) {

        console.error(
            "Clipboard error:",
            error
        );

    }
}

/* ==========================================
   Copy Button Support
========================================== */

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

        copyToClipboard(value);
    }
);

/* ==========================================
   Confirm Actions
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
            ) || "Are you sure?";

        const confirmed =
            window.confirm(message);

        if (!confirmed) {
            event.preventDefault();
        }
    }
);

/* ==========================================
   Auto Refresh Tables
========================================== */

function autoRefresh() {

    const interval =
        document.body.dataset.refresh;

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
        () => window.location.reload(),
        seconds * 1000
    );
}

autoRefresh();

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
                this.value.toLowerCase();

            const rows =
                document.querySelectorAll(
                    "[data-filter-row]"
                );

            rows.forEach(row => {

                const text =
                    row.innerText.toLowerCase();

                row.style.display =
                    text.includes(value)
                        ? ""
                        : "none";

            });
        }
    );
}

initializeFilters();

/* ==========================================
   AJAX Refresh Button
========================================== */

async function refreshSubscription(id) {

    try {

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

        window.location.reload();

    } catch (error) {

        alert(
            "Failed to refresh subscription."
        );

        console.error(error);
    }
}

/* ==========================================
   Loading Buttons
========================================== */

document.addEventListener(
    "submit",
    function (event) {

        const form = event.target;

        if (!(form instanceof HTMLFormElement)) {
            return;
        }

        const button =
            form.querySelector(
                "button[type='submit']"
            );

        if (!button) {
            return;
        }

        button.disabled = true;

        const original =
            button.innerHTML;

        button.innerHTML =
            "Please wait...";

        setTimeout(
            () => {
                button.disabled = false;
                button.innerHTML = original;
            },
            10000
        );
    }
);