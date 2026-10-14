// Phosphors CRT site — the only script: the mobile menu toggle and the demo player.
(function () {
  var toggle = document.querySelector('.nav-toggle');
  var links = document.getElementById('nav-links');
  if (!toggle || !links) return;
  toggle.addEventListener('click', function () {
    var open = links.classList.toggle('open');
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  links.addEventListener('click', function (e) {
    if (e.target.tagName === 'A') {
      links.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });
})();

// Demo player. Shows a self-hosted poster and only loads YouTube (privacy-enhanced
// mode) once someone presses play, so the page itself sets no cookies.
// Without JS every poster and thumbnail is a plain link to the video on YouTube.
(function () {
  var player = document.getElementById('demo-player');
  var caption = document.getElementById('demo-caption');
  var list = document.querySelector('.demo-list');
  if (!player || !list) return;
  var poster = player.querySelector('.demo-poster');
  var posterImg = poster.querySelector('img');

  function play(id) {
    var frame = document.createElement('iframe');
    frame.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) +
      '?autoplay=1&rel=0&playsinline=1&modestbranding=1';
    frame.title = 'Phosphors CRT demo video';
    frame.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
    frame.allowFullscreen = true;
    var old = player.querySelector('iframe');
    if (old) old.remove();
    poster.hidden = true;
    player.appendChild(frame);
  }

  poster.addEventListener('click', function (e) {
    e.preventDefault();
    play(poster.dataset.video);
  });

  list.addEventListener('click', function (e) {
    var a = e.target.closest('a[data-video]');
    if (!a) return;
    e.preventDefault();
    list.querySelectorAll('a[aria-current]').forEach(function (x) { x.removeAttribute('aria-current'); });
    a.setAttribute('aria-current', 'true');
    caption.textContent = a.dataset.caption;
    poster.href = a.href;
    poster.dataset.video = a.dataset.video;
    poster.setAttribute('aria-label', 'Play: ' + a.textContent.trim());
    posterImg.src = a.dataset.poster;
    // Once a video is playing, picking another one plays it straight away.
    if (player.querySelector('iframe')) {
      play(a.dataset.video);
    } else if (window.matchMedia('(max-width: 980px)').matches) {
      player.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  });
})();
