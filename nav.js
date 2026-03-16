// Shared nav scroll & mobile toggle
const navbar = document.getElementById('navbar');
if (navbar) {
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 40);
  });
}

function toggleMobileNav() {
  const links = document.querySelector('.nav-links');
  if (!links) return;
  const isOpen = links.style.display === 'flex';
  if (isOpen) {
    links.style.display = 'none';
  } else {
    Object.assign(links.style, {
      display: 'flex',
      flexDirection: 'column',
      position: 'absolute',
      top: '68px', left: '0', right: '0',
      background: 'rgba(8,21,43,0.98)',
      backdropFilter: 'blur(16px)',
      padding: '24px 32px',
      borderBottom: '1px solid rgba(201,150,42,0.18)',
      zIndex: '99',
      gap: '20px'
    });
  }
}
