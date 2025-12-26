// Nothing to see here, move along...
window.spawnCookieParticles = () => {
  const cookie = document.getElementById("blazor");
  if (!cookie) return;

  const rect = cookie.getBoundingClientRect();
  const originX = rect.left + rect.width / 2;
  const originY = rect.top + rect.height / 2;

  const count = 22;
  const gravity = 1100;
  const lifetime = 900;

  for (let i = 0; i < count; i++) {
    const el = document.createElement("div");
    el.className = "cookie-particle";

    const angle = (Math.PI * 2 * i) / count + (Math.random() - 0.5) * 0.8;
    const speed = 380 + Math.random() * 180;
    const vx = Math.cos(angle) * speed;
    const vy = Math.sin(angle) * speed - 240;
    const spin = Math.random() * 160 - 80;
    const start = performance.now();

    el.style.left = `${originX}px`;
    el.style.top = `${originY}px`;
    document.body.appendChild(el);

    const step = (now) => {
      const t = Math.min(now - start, lifetime);
      const dt = t / 1000;
      const x = Math.floor(vx * dt);
      const y = Math.floor(vy * dt + 0.5 * gravity * dt * dt);
      const opacity = 1 - t / lifetime;
      el.style.transform = `translate(${x - 16}px, ${y - 16}px) scale(${
        0.6 + 0.5 * opacity
      }) rotate(${spin * dt}deg)`;
      el.style.opacity = opacity;
      if (t < lifetime) {
        requestAnimationFrame(step);
      } else {
        el.remove();
      }
    };

    requestAnimationFrame(step);
  }
};
