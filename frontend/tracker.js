(function () {
  const sessionId = Math.random().toString(36).substring(2);
  const page = window.location.pathname;
  const startTime = Date.now();

  // Send page view
  sendEvent("page_view");

  // Click tracking
  document.addEventListener("click", (e) => {
    const element = e.target.tagName + (e.target.id ? "#" + e.target.id : "");
    sendEvent("click", element);
  });

  // Scroll tracking
  let maxScroll = 0;
  window.addEventListener("scroll", () => {
    const currentScroll = (window.scrollY + window.innerHeight) / document.body.scrollHeight;
    if (currentScroll > maxScroll) {
      maxScroll = currentScroll;
    }
  });

  // Before leaving the page (session end)
  window.addEventListener("beforeunload", () => {
    const duration = (Date.now() - startTime) / 1000;
    sendEvent("session_end", null, maxScroll, duration);
  });

  function sendEvent(event_type, element = "", scroll_depth = 0, duration = 0) {
    fetch("http://lugx.local:32173/track", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        event_type,
        page,
        element,
        scroll_depth,
        duration,
        session_id: sessionId
      })
    }).catch(err => console.log("Tracking failed:", err));
  }
})();
