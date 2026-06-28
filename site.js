// Mobile nav toggle for the inner pages.
document.addEventListener('click', e => {
  const toggle = e.target.closest('.navtoggle');
  const links = document.querySelector('.navlinks');
  if (toggle && links) { links.classList.toggle('open'); return; }
  if (links && !e.target.closest('.topnav')) links.classList.remove('open');
});
