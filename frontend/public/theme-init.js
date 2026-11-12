// Apply the saved appearance before the app paints, including on direct links.
try {
  document.documentElement.dataset.theme =
    localStorage.getItem("mizan-theme") === "light" ? "light" : "dark";
} catch {
  document.documentElement.dataset.theme = "dark";
}
