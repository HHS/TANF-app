// /components/navigation.js
class ShutDownBanner extends HTMLElement {
  connectedCallback() {
    fetch('components/shutdown-banner.html')
      .then(res => res.text())
      .then(html => {
        this.innerHTML = html;
      })
      .catch(err => {
        this.innerHTML = '<p>Error loading navigation.</p>';
        console.error('Nav load error:', err);
      });
  }
}

customElements.define('shut-down', ShutDownBanner);


