<script>
(() => {
  function isTypingTarget(el) {
    if (!el) return false;
    const tag = (el.tagName || "").toLowerCase();
    return el.isContentEditable || tag === "input" || tag === "textarea" || tag === "select";
  }

  function navigateTo(rel) {
    const headLink = document.querySelector(`link[rel='${rel}']`);
    if (headLink && headLink.href) {
      window.location.href = headLink.href;
      return true;
    }

    const navSelector =
      rel === "prev"
        ? ".nav-page-previous a[href], a.prev-page[href], a[rel='prev'][href]"
        : ".nav-page-next a[href], a.next-page[href], a[rel='next'][href]";
    const navLink = document.querySelector(navSelector);
    if (navLink && navLink.href) {
      window.location.href = navLink.href;
      return true;
    }

    return false;
  }

  document.addEventListener("keydown", (event) => {
    if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    if (isTypingTarget(document.activeElement)) return;

    if (event.key === "ArrowLeft") {
      if (navigateTo("prev")) {
        event.preventDefault();
      }
    }

    if (event.key === "ArrowRight") {
      if (navigateTo("next")) {
        event.preventDefault();
      }
    }
  });
})();
</script>
