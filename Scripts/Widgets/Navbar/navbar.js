/**
 * Standalone modern replacement for iWeb navbar.js
 * No Prototype.js or external XML feeds required.
 */
(function () {
  const NAV_ITEMS = [
    { title: "About", url: "About.html" },
    { title: "Publications", url: "Publications.html" }
  ];

  // Preserves original iWeb navbar styling and active colors
  const NAVBAR_CSS = `
    .navbar {
      font-family: 'Helvetica Neue', Arial, sans-serif;
      font-size: .8em;
      color: #666666;
      line-height: 30px;
      border-bottom: 3px solid #ccc;
    }
    .navbar-bg {
      text-align: right;
    }
    .navbar-bg ul {
      list-style: none;
      margin: 0px;
      padding: 0px;
    }
    .navbar-bg li {
      list-style-type: none;
      display: inline;
      padding: 0px 5px 0px 0px;
    }
    .navbar-bg li a {
      text-decoration: none;
      padding: 10px;
      color: #666666;
      font-weight: bold;
    }
    .navbar-bg li a:hover {
      color: #999999;
      text-decoration: none;
    }
    .navbar-bg li.current-page a {
      color: #66ABC5;
      text-decoration: none;
      cursor: default;
    }
  `;

  function injectCSS() {
    if (document.getElementById("modern-navbar-css")) return;
    const style = document.createElement("style");
    style.id = "modern-navbar-css";
    style.textContent = NAVBAR_CSS;
    document.head.appendChild(style);
  }

  function renderNavbar() {
    injectCSS();

    const navList =
      document.getElementById("widget0-navbar-list") ||
      document.querySelector(".navbar-list");

    if (!navList) return;

    // Detect active page (About is active on root '/', index.html, or About.html)
    const currentPath = window.location.pathname.toLowerCase();
    const isPublications = currentPath.includes("publications");
    const isAbout = !isPublications;

    navList.innerHTML = "";

    NAV_ITEMS.forEach((item) => {
      const li = document.createElement("li");
      const a = document.createElement("a");

      a.textContent = item.title;

      const isCurrent =
        (item.title === "About" && isAbout) ||
        (item.title === "Publications" && isPublications);

      if (isCurrent) {
        li.className = "current-page";
        // Matches iWeb behavior: active page is not clickable
      } else {
        li.className = "noncurrent-page";
        a.href = item.url;
      }

      li.appendChild(a);
      navList.appendChild(li);
    });
  }

  // Compatible with the inline `new NavBar(...)` call in your existing HTML
  window.NavBar = function () {
    renderNavbar();
  };

  // Also executes automatically when the DOM loads
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", renderNavbar);
  } else {
    renderNavbar();
  }
})();