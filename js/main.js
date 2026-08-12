(function () {
  'use strict';

  // Statični podaci o projektima. Galerije su u ovoj fazi placeholderi (vidi
  // komentar na vrhu index.html "ZA POSLIJE") — kad klijent pošalje prave
  // fotografije, ovdje se labeli zamjenjuju putanjama do slika.
  var PROJECTS = [
    {
      naslov: 'Kuhinje po mjeri',
      lokacija: 'Slavonski Brod',
      dimenzije: 'po izmjeri prostora',
      izvedba: 'Fronta design',
      galerija: [
        'Fotografija — kuhinja, radna ploča i otok',
        'Fotografija — kuhinja, gornji elementi',
        'Fotografija — kuhinja, ugrađeni aparati'
      ]
    },
    {
      naslov: 'Ugradbeni ormari i garderobe',
      lokacija: 'Slavonski Brod',
      dimenzije: 'po izmjeri prostora',
      izvedba: 'Fronta design',
      galerija: [
        'Fotografija — ugradbeni ormar, cijeli pogled',
        'Fotografija — ugradbeni ormar, detalj okova',
        'Fotografija — garderoba, unutrašnjost'
      ]
    },
    {
      naslov: 'Dnevne sobe i dnevni boravak',
      lokacija: 'Slavonski Brod',
      dimenzije: 'po izmjeri prostora',
      izvedba: 'Fronta design',
      galerija: [
        'Fotografija — dnevni boravak, TV komoda',
        'Fotografija — dnevni boravak, police',
        'Fotografija — dnevni boravak, detalj izrade'
      ]
    },
    {
      naslov: 'Spavaće te dječje i radne sobe',
      lokacija: 'Slavonski Brod',
      dimenzije: 'po izmjeri prostora',
      izvedba: 'Fronta design',
      galerija: [
        'Fotografija — spavaća soba, ormar',
        'Fotografija — dječja soba, radni stol',
        'Fotografija — radna soba, police'
      ]
    }
  ];

  document.addEventListener('DOMContentLoaded', function () {
    initMobileMenu();
    initGalleryModal();
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

  // Hrvatska sklonidba broja fotografija: 1 → "fotografija", 2–4 → "fotografije",
  // 5+ → "fotografija" (uz iznimku brojeva 11–14 koji su uvijek "fotografija").
  function brojFotografija(n) {
    var zadnja2 = n % 100;
    var zadnja1 = n % 10;
    if (zadnja2 > 10 && zadnja2 < 20) return n + ' fotografija';
    if (zadnja1 === 1) return n + ' fotografija';
    if (zadnja1 >= 2 && zadnja1 <= 4) return n + ' fotografije';
    return n + ' fotografija';
  }

  function initGalleryModal() {
    var modal = document.getElementById('projektModal');
    var lightbox = document.getElementById('lightbox');
    if (!modal || !lightbox) return;

    var modalCount = document.getElementById('modalCount');
    var modalTitle = document.getElementById('modalTitle');
    var modalLokacija = document.getElementById('modalLokacija');
    var modalDimenzije = document.getElementById('modalDimenzije');
    var modalIzvedba = document.getElementById('modalIzvedba');
    var modalGallery = document.getElementById('modalGallery');

    var lightboxStage = document.getElementById('lightboxStage');
    var lightboxCount = document.getElementById('lightboxCount');
    var lightboxPlaceholderLabel = document.getElementById('lightboxPlaceholderLabel');
    var lightboxClose = document.getElementById('lightboxClose');
    var lightboxPrev = document.getElementById('lightboxPrev');
    var lightboxNext = document.getElementById('lightboxNext');

    var activeProjectIndex = null;
    var activeZoomIndex = null;

    function openModal(index) {
      var projekt = PROJECTS[index];
      if (!projekt) return;
      activeProjectIndex = index;

      modalCount.textContent = brojFotografija(projekt.galerija.length);
      modalTitle.textContent = projekt.naslov;
      modalLokacija.textContent = projekt.lokacija;
      modalDimenzije.textContent = projekt.dimenzije;
      modalIzvedba.textContent = projekt.izvedba;

      modalGallery.innerHTML = '';
      projekt.galerija.forEach(function (label, i) {
        var figure = document.createElement('figure');
        figure.className = 'gallery-item';

        var media = document.createElement('div');
        media.className = 'gallery-media';

        var placeholder = document.createElement('div');
        placeholder.className = 'photo-placeholder';
        placeholder.setAttribute('aria-hidden', 'true');
        var span = document.createElement('span');
        span.textContent = label;
        placeholder.appendChild(span);
        media.appendChild(placeholder);

        var zoomBtn = document.createElement('button');
        zoomBtn.type = 'button';
        zoomBtn.className = 'gallery-zoom';
        zoomBtn.setAttribute('aria-label', 'Povećaj sliku');
        zoomBtn.dataset.zoomIndex = String(i);
        var zoomSpan = document.createElement('span');
        zoomSpan.textContent = 'Povećaj';
        zoomBtn.appendChild(zoomSpan);
        media.appendChild(zoomBtn);

        var figcaption = document.createElement('figcaption');
        figcaption.textContent = String(i + 1).padStart(2, '0');

        figure.appendChild(media);
        figure.appendChild(figcaption);
        modalGallery.appendChild(figure);
      });

      modal.hidden = false;
      document.body.style.overflow = 'hidden';
    }

    function closeModal() {
      modal.hidden = true;
      activeProjectIndex = null;
      closeLightbox();
      document.body.style.overflow = '';
    }

    function openLightbox(zoomIndex) {
      if (activeProjectIndex == null) return;
      var total = PROJECTS[activeProjectIndex].galerija.length;
      activeZoomIndex = ((zoomIndex % total) + total) % total;
      renderZoom();
      lightbox.hidden = false;
    }

    function renderZoom() {
      var projekt = PROJECTS[activeProjectIndex];
      var total = projekt.galerija.length;
      lightboxCount.textContent = (activeZoomIndex + 1) + ' / ' + total;
      lightboxPlaceholderLabel.textContent = projekt.galerija[activeZoomIndex];
    }

    function closeLightbox() {
      lightbox.hidden = true;
      activeZoomIndex = null;
    }

    function stepZoom(delta) {
      if (activeProjectIndex == null || activeZoomIndex == null) return;
      var total = PROJECTS[activeProjectIndex].galerija.length;
      activeZoomIndex = ((activeZoomIndex + delta) % total + total) % total;
      renderZoom();
    }

    // Otvaranje modala klikom na naslov projekta / "Galerija →"
    document.querySelectorAll('.projekt-open').forEach(function (btn) {
      btn.addEventListener('click', function () {
        openModal(parseInt(btn.dataset.project, 10));
      });
    });

    // Zatvaranje modala: backdrop, ✕, "Zatražite ponudu →"
    modal.querySelectorAll('[data-close-modal]').forEach(function (el) {
      el.addEventListener('click', closeModal);
    });

    // Klik na "Povećaj" — delegacija jer se galerija generira dinamički
    modalGallery.addEventListener('click', function (e) {
      var btn = e.target.closest('.gallery-zoom');
      if (!btn) return;
      openLightbox(parseInt(btn.dataset.zoomIndex, 10));
    });

    lightboxClose.addEventListener('click', closeLightbox);
    lightboxPrev.addEventListener('click', function () { stepZoom(-1); });
    lightboxNext.addEventListener('click', function () { stepZoom(1); });
    lightboxStage.addEventListener('click', closeLightbox);

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        if (!lightbox.hidden) closeLightbox();
        else if (!modal.hidden) closeModal();
        return;
      }
      if (!lightbox.hidden) {
        if (e.key === 'ArrowRight') stepZoom(1);
        if (e.key === 'ArrowLeft') stepZoom(-1);
      }
    });
  }

  function initForm() {
    var form = document.getElementById('kontaktForma');
    var thankYou = document.getElementById('thankYou');
    var resetBtn = document.getElementById('resetForma');
    if (!form || !thankYou) return;

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      form.hidden = true;
      thankYou.hidden = false;
    });

    if (resetBtn) {
      resetBtn.addEventListener('click', function () {
        form.reset();
        thankYou.hidden = true;
        form.hidden = false;
      });
    }
  }
})();
