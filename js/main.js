(function () {
  'use strict';

  // Statični podaci o projektima. Svaka galerijska stavka ima src (putanja do
  // prave fotografije u images/) i label (koristi se kao alt/aria-label).
  var PROJECTS = [
    {
      naslov: 'Kuhinje po mjeri',
      lokacija: 'Slavonski Brod',
      dimenzije: 'po izmjeri prostora',
      izvedba: 'Fronta design',
      galerija: [
        { src: 'images/kuhinje-01.jpg', label: 'Kuhinja — bijela mat, ugrađeni hladnjak' },
        { src: 'images/kuhinje-20.jpg', label: 'Kuhinja — bijela mat, kutni pogled' },
        { src: 'images/kuhinje-02.jpg', label: 'Kuhinja — zelena mat, visoka kolona' },
        { src: 'images/kuhinje-03.jpg', label: 'Kuhinja — zelena mat, L raspored' },
        { src: 'images/kuhinje-04.jpg', label: 'Kuhinja — siva mat, L raspored' },
        { src: 'images/kuhinje-05.jpg', label: 'Kuhinja — grafit, barski pult' },
        { src: 'images/kuhinje-06.jpg', label: 'Kuhinja — grafit, kameni radni pult' },
        { src: 'images/kuhinje-07.jpg', label: 'Kuhinja — industrijski stil, opeka i napa' },
        { src: 'images/kuhinje-08.jpg', label: 'Kuhinja — hrast, ugrađena pećnica' },
        { src: 'images/kuhinje-09.jpg', label: 'Kuhinja — bijela mat, zlatni detalji' },
        { src: 'images/kuhinje-10.jpg', label: 'Kuhinja — bijela mat, crni naglasak' },
        { src: 'images/kuhinje-11.jpg', label: 'Kuhinja — bijela mat, barski pult' },
        { src: 'images/kuhinje-12.jpg', label: 'Kuhinja — hrast, barski pult' },
        { src: 'images/kuhinje-13.jpg', label: 'Kuhinja — bijela mat, otvoreni prostor s otokom' },
        { src: 'images/kuhinje-14.jpg', label: 'Kuhinja — zelena mat, kutna kolona' },
        { src: 'images/kuhinje-15.jpg', label: 'Kuhinja — zelena mat, blagovaonski stol' },
        { src: 'images/kuhinje-16.jpg', label: 'Kuhinja — bijela mat, viseća rasvjeta' },
        { src: 'images/kuhinje-17.jpg', label: 'Kuhinja — bijela mat, detalj radne plohe' },
        { src: 'images/kuhinje-18.jpg', label: 'Kuhinja — bijela mat, pogled od stola' },
        { src: 'images/kuhinje-19.jpg', label: 'Kuhinja — bijela mat, detalj visoke kolone' }
      ]
    },
    {
      naslov: 'Ormari po mjeri',
      lokacija: 'Slavonski Brod',
      dimenzije: 'po izmjeri prostora',
      izvedba: 'Fronta design',
      galerija: [
        { src: 'images/ormari-01.jpg', label: 'Ugradbeni ormar — hodnik' },
        { src: 'images/ormari-02.jpg', label: 'Ugradbeni ormar — spavaća soba' },
        { src: 'images/ormari-03.jpg', label: 'Ugradbeni ormar — unutrašnjost s policama' },
        { src: 'images/ormari-04.jpg', label: 'Predsoblje — ormar s ogledalom' },
        { src: 'images/ormari-05.jpg', label: 'Ugradbeni ormar — kutni raspored' },
        { src: 'images/ormari-06.jpg', label: 'Ugradbeni ormar — detalj unutrašnjosti' }
      ]
    },
    {
      naslov: 'Komode i ladičari',
      lokacija: 'Slavonski Brod',
      dimenzije: 'po izmjeri prostora',
      izvedba: 'Fronta design',
      galerija: [
        { src: 'images/dnevne-cover.jpg', label: 'TV komoda — bijeli lak' },
        { src: 'images/dnevne-01.jpg', label: 'Komoda s kliznim vratima' },
        { src: 'images/dnevne-02.jpg', label: 'Ladičar — bočni pogled' },
        { src: 'images/kupaonica-01.jpg', label: 'Kupaonski element s ladicama' }
      ]
    },
    {
      naslov: 'Radne Sobe',
      lokacija: 'Slavonski Brod',
      dimenzije: 'po izmjeri prostora',
      izvedba: 'Fronta design',
      galerija: [
        { src: 'images/radne-01.jpg', label: 'Radni stol u L izvedbi' },
        { src: 'images/radne-cover.jpg', label: 'Radni stol — tamni dekor' }
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
    var lightboxImage = document.getElementById('lightboxImage');
    var lightboxPlaceholder = document.getElementById('lightboxPlaceholder');
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
      projekt.galerija.forEach(function (item, i) {
        var figure = document.createElement('figure');
        figure.className = 'gallery-item';

        var media = document.createElement('div');
        media.className = 'gallery-media';

        if (item.src) {
          var img = document.createElement('img');
          img.src = item.src;
          img.alt = item.label || '';
          img.loading = 'lazy';
          media.appendChild(img);
        } else {
          var placeholder = document.createElement('div');
          placeholder.className = 'photo-placeholder';
          placeholder.setAttribute('aria-hidden', 'true');
          var span = document.createElement('span');
          span.textContent = item.label || '';
          placeholder.appendChild(span);
          media.appendChild(placeholder);
        }

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
      var item = projekt.galerija[activeZoomIndex];
      lightboxCount.textContent = (activeZoomIndex + 1) + ' / ' + total;
      if (item.src) {
        lightboxImage.src = item.src;
        lightboxImage.alt = item.label || '';
        lightboxImage.hidden = false;
        lightboxPlaceholder.hidden = true;
      } else {
        lightboxImage.hidden = true;
        lightboxPlaceholder.hidden = false;
        lightboxPlaceholderLabel.textContent = item.label || '';
      }
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
