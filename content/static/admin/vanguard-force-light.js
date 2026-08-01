/**
 * Force Vanguard admin to stay in light theme.
 * Unfold persists the last theme in localStorage and that was winning over THEME="light".
 */
(function () {
  try {
    localStorage.setItem("adminTheme", JSON.stringify("light"));
  } catch (_) {
    /* ignore */
  }

  const apply = () => {
    document.documentElement.classList.remove("dark");
    document.documentElement.classList.add("light");
  };

  apply();
  document.addEventListener("DOMContentLoaded", apply);
  // Alpine may re-apply the persisted theme after boot — nudge it back.
  window.addEventListener("load", () => {
    apply();
    setTimeout(apply, 50);
    setTimeout(apply, 250);
  });
})();
