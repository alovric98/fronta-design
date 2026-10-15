(function () {
  'use strict';

  var WEB3FORMS_ENDPOINT = 'https://api.web3forms.com/submit';
  var PORUKA_GRESKE = 'Slanje nije uspjelo. Pokušajte ponovno ili nas nazovite izravno na 097 6113 362.';

  document.addEventListener('DOMContentLoaded', function () {
    initMobileMenu();
    initCtaBar();
    initProjekti();
    initForm();
  });

  function initMobileMenu() {
    var toggle = document.getElementById('menuToggle');
    var nav = document.getElementById('mobileNav');
    if (!toggle || !nav) return;

    toggle.addEventListener('click', function () {
      var isOpen = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', String(isOpen));
    });

    nav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        nav.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // Mobile call/quote bar: shown once the hero has scrolled away, hidden again while the contact section is on screen.
  function initCtaBar() {
    var bar = document.getElementById('ctaBar');
    var hero = document.querySelector('.hero');
    var kontakt = document.getElementById('kontakt');
    if (!bar || !hero || !kontakt) return;

    var heroVisible = true;
    var kontaktVisible = false;
    // The top margin matches the sticky header: the hero's last pixels hide behind it.
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.target === hero) heroVisible = e.isIntersecting;
        else kontaktVisible = e.isIntersecting;
      });
      bar.classList.toggle('is-visible', !heroVisible && !kontaktVisible);
    }, { rootMargin: '-60px 0px 0px 0px' });
    io.observe(hero);
    io.observe(kontakt);
  }

  function initProjekti() {
    var grid = document.getElementById('projektiGrid');
    var lightbox = document.getElementById('lightbox');
    if (!grid || !lightbox) return;

    var tiles = Array.prototype.slice.call(grid.children);
    var total = tiles.length;
    var more = document.getElementById('projektiMore');
    var moreBtn = document.getElementById('projektiMoreBtn');
    var counter = document.getElementById('projektiCounter');
    var mobile = window.matchMedia('(max-width: 639px)');
    var moreStep = 0;

    // Start with 4 (mobile) or 6 (desktop) photos; the first "Show more" click reveals 12 more, the second everything.
    function startCount() { return mobile.matches ? 4 : 6; }
    function visibleCount() {
      if (moreStep === 0) return startCount();
      if (moreStep === 1) return startCount() + 12;
      return total;
    }

    function render() {
      var visible = Math.min(visibleCount(), total);
      tiles.forEach(function (tile, i) { tile.hidden = i >= visible; });
      counter.textContent = 'Prikazano ' + visible + ' od ' + total;
      more.hidden = total <= startCount();
      // Once everything is shown the same button collapses the gallery back to the start.
      moreBtn.textContent = visible >= total ? 'Skrati prikaz' : 'Prikaži više';
    }

    moreBtn.addEventListener('click', function () {
      if (Math.min(visibleCount(), total) >= total) {
        moreStep = 0;
        render();
        // Collapsing leaves the viewport at the bottom of the old gallery; bring the top back (smooth via CSS).
        document.getElementById('projekti').scrollIntoView();
        return;
      }
      // Only tiles revealed by a click get the fade-in; the ones already on screen must not flicker.
      var from = Math.min(visibleCount(), total);
      moreStep++;
      tiles.slice(from, Math.min(visibleCount(), total)).forEach(function (tile) { tile.classList.add('is-new'); });
      render();
    });
    mobile.addEventListener('change', render);
    render();

    var figure = document.getElementById('lightboxFigure');
    var lightboxImage = document.getElementById('lightboxImage');
    var lightboxPlaceholder = document.getElementById('lightboxPlaceholder');
    var lightboxPlaceholderLabel = document.getElementById('lightboxPlaceholderLabel');
    var lightboxClose = document.getElementById('lightboxClose');
    var lightboxPrev = document.getElementById('lightboxPrev');
    var lightboxNext = document.getElementById('lightboxNext');

    var current = 0;
    var opener = null;

    function show(index) {
      current = index;
      var tile = tiles[index];
      var img = tile.querySelector('img');
      if (img) {
        lightboxImage.src = img.src;
        lightboxImage.alt = img.alt;
        lightboxImage.hidden = false;
        lightboxPlaceholder.hidden = true;
      } else {
        lightboxImage.hidden = true;
        lightboxPlaceholder.hidden = false;
        lightboxPlaceholderLabel.textContent = tile.textContent.trim();
      }
      lightbox.setAttribute('aria-label', 'Fotografija ' + (index + 1) + ' od ' + total);
      // No wrap-around: the first photo has no "previous", the last has no "next".
      lightboxPrev.hidden = index === 0;
      lightboxNext.hidden = index === total - 1;
      if (document.activeElement && document.activeElement.hidden) lightboxClose.focus();
    }

    function step(delta) {
      var next = current + delta;
      if (next >= 0 && next < total) show(next);
    }

    function openLightbox(index, from) {
      opener = from;
      show(index);
      lightbox.hidden = false;
      document.body.style.overflow = 'hidden';
      lightboxClose.focus();
    }

    function closeLightbox() {
      lightbox.hidden = true;
      document.body.style.overflow = '';
      if (opener) opener.focus();
    }

    grid.addEventListener('click', function (e) {
      var btn = e.target.closest('.projekt-photo');
      if (btn) openLightbox(tiles.indexOf(btn.closest('li')), btn);
    });

    lightboxPrev.addEventListener('click', function () { step(-1); });
    lightboxNext.addEventListener('click', function () { step(1); });
    lightboxClose.addEventListener('click', closeLightbox);
    // Tap on the dark area around the photo closes it.
    lightbox.addEventListener('click', function (e) {
      if (!figure.contains(e.target)) closeLightbox();
    });

    document.addEventListener('keydown', function (e) {
      if (lightbox.hidden) return;
      if (e.key === 'Escape') closeLightbox();
      if (e.key === 'ArrowRight') step(1);
      if (e.key === 'ArrowLeft') step(-1);
    });

    // Swipe: left = next photo, right = previous.
    var swipeStartX = null;
    lightbox.addEventListener('pointerdown', function (e) { swipeStartX = e.clientX; });
    lightbox.addEventListener('pointerup', function (e) {
      if (swipeStartX == null) return;
      var dx = e.clientX - swipeStartX;
      swipeStartX = null;
      if (Math.abs(dx) > 50) step(dx < 0 ? 1 : -1);
    });
  }

  function initForm() {
    var form = document.getElementById('kontaktForma');
    var thankYou = document.getElementById('thankYou');
    var resetBtn = document.getElementById('resetForma');
    if (!form || !thankYou) return;

    var greska = document.getElementById('formaGreska');
    var submitBtn = form.querySelector('button[type="submit"]');
    var submitLabel = submitBtn ? submitBtn.textContent : '';
    var slanjeUTijeku = false;

    function prikaziGresku(poruka) {
      if (!greska) return;
      greska.textContent = poruka;
      greska.hidden = false;
    }

    function sakrijGresku() {
      if (!greska) return;
      greska.hidden = true;
      greska.textContent = '';
    }

    // Zaključava formu dok traje mrežni poziv — spriječava dupli submit
    // (dvoklik na gumb ili Enter dok prvi zahtjev još visi).
    function zakljucaj(zakljucano) {
      slanjeUTijeku = zakljucano;
      if (!submitBtn) return;
      submitBtn.disabled = zakljucano;
      submitBtn.textContent = zakljucano ? 'Šaljemo…' : submitLabel;
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (slanjeUTijeku) return;
      sakrijGresku();
      zakljucaj(true);

      var podaci = Object.fromEntries(new FormData(form).entries());

      fetch(WEB3FORMS_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(podaci)
      })
        .then(function (res) {
          // res.json() puca ako server vrati HTML umjesto JSON-a (npr. proxy greška);
          // taj reject hvata .catch ispod, isto kao i mrežni pad.
          return res.json().then(function (json) {
            return { ok: res.ok, json: json };
          });
        })
        .then(function (odgovor) {
          if (!odgovor.ok || odgovor.json.success !== true) {
            throw new Error('Web3Forms je odbio zahtjev.');
          }
          form.reset();
          form.hidden = true;
          thankYou.hidden = false;
        })
        .catch(function () {
          prikaziGresku(PORUKA_GRESKE);
        })
        .then(function () {
          zakljucaj(false);
        });
    });

    if (resetBtn) {
      resetBtn.addEventListener('click', function () {
        form.reset();
        sakrijGresku();
        thankYou.hidden = true;
        form.hidden = false;
      });
    }
  }
})();
