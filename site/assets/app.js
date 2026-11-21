(function () {
  "use strict";

  var D = window.CLASS_ARCHIVE;
  var $ = function (id) { return document.getElementById(id); };
  if (!D) {
    document.body.insertAdjacentHTML("afterbegin", "<p style=\"padding:24px\">站点数据暂未载入。</p>");
    return;
  }

  var DEFAULT_FILE_LIMIT = 24;
  var ROMAN = ["I", "II", "III", "IV", "V", "VI"];
  var state = {
    volFilter: "vol-1",
    catFilter: "all",
    query: "",
    expandFiles: false,
    activeSlug: null,
    lastTrigger: null
  };

  var ESSAY_MAP = new Map();
  D.essays.forEach(function (e, idx) {
    ESSAY_MAP.set(e.slug, { essay: e, index: idx });
  });

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function badgeClass(badge) {
    if (badge === "21F") return "badge badge-21f";
    if (badge === "21C") return "badge badge-21c";
    return "badge";
  }

  function stripTitlePrefix(text, title) {
    var t = String(text == null ? "" : text).replace(/^\s+/, "");
    var tt = String(title == null ? "" : title).replace(/\s+/g, "");
    if (!tt) return t;
    var probe = t.replace(/\s+/g, "");
    if (probe.indexOf(tt) !== 0) return t;
    var count = 0, i = 0;
    while (i < t.length && count < tt.length) {
      if (!/\s/.test(t.charAt(i))) count++;
      i++;
    }
    return t.slice(i).replace(/^[\s，,、。：:；;！!？?]+/, "");
  }

  function renderHeroStats() {
    var m = D.meta || {};
    var items = [
      { num: "2", label: "个班级（21F → 21C）", cls: "f" },
      { num: String(m.groupsCount || 29), label: "个班级与课程群" },
      { num: String(m.totalGroupFiles || 894), label: "份群流转资料", cls: "c" },
      { num: "4", label: "年花都岁月" }
    ];
    $("stat-pills").innerHTML = items.map(function (it) {
      return '<div class="stat' + (it.cls ? " stat-" + it.cls : "") + '">' +
        '<span class="stat-num">' + esc(it.num) + "</span>" +
        '<span class="stat-label">' + esc(it.label) + "</span>" +
        "</div>";
    }).join("");
    if ($("groups-toggle-label")) {
      $("groups-toggle-label").textContent = "查看 " + (m.groupsCount || 29) + " 个班级与课程群概览";
    }
  }

  function renderChronicle() {
    var vols = D.chronicle || [];
    if (state.volFilter !== "all" && !vols.some(function (v) { return v.id === state.volFilter; })) {
      state.volFilter = vols.length ? vols[0].id : "all";
    }
    var totalEv = vols.reduce(function (acc, v) { return acc + (v.events ? v.events.length : 0); }, 0);
    var tabs = vols.map(function (v) {
      var cnt = v.events ? v.events.length : 0;
      return { id: v.id, label: v.label + " (" + cnt + ")" };
    }).concat([{ id: "all", label: "全部五卷 (" + totalEv + ")" }]);

    $("vol-tabs").innerHTML = tabs.map(function (t) {
      var sel = state.volFilter === t.id ? "true" : "false";
      return '<button type="button" class="tab-btn" role="tab" aria-selected="' + sel + '" data-vol="' + esc(t.id) + '">' + esc(t.label) + "</button>";
    }).join("");

    var shown = state.volFilter === "all"
      ? vols
      : vols.filter(function (v) { return v.id === state.volFilter; });

    $("timeline-list").innerHTML = shown.map(function (v) {
      var no = String(vols.indexOf(v) + 1).padStart(2, "0");
      var kws = (v.keywords || []).map(function (k) {
        return '<span class="kw-tag">' + esc(k) + "</span>";
      }).join("");
      var evs = (v.events || []).map(function (ev) {
        var extraLink = ev.link && ev.link.url
          ? '<a class="event-special-link" href="' + esc(ev.link.url) + '" target="_blank" rel="noopener noreferrer">' + esc(ev.link.label) + "</a>"
          : "";
        return '<div class="event-item">' +
          '<div class="event-head">' +
            '<span class="event-date mono">' + esc(ev.date) + "</span>" +
            '<span class="event-title">' + esc(ev.title) + "</span>" +
          "</div>" +
          '<div class="event-body">' + (ev.html || "") + "</div>" +
          extraLink +
        "</div>";
      }).join("");

      // Photo-ready slot: renders per-volume memory anchors
      var photosHtml = "";
      if (v.photos && v.photos.length) {
        if (v.id === "vol-1") {
          var fBig = v.photos.filter(function (ph) { return ph.id === "ph-f-junxun"; })[0];
          var fRest = v.photos.filter(function (ph) { return ph !== fBig; });
          photosHtml = '<div class="vol-photos-wrap" id="f-gallery">' +
            '<div class="vol-photos-head">' +
              '<strong>本卷影像锚点 · ' + v.photos.length + ' 帧</strong>' +
              '<span>四帧日常与军训大合影 · 点击可暗房放大</span>' +
            '</div>' +
            '<div class="f-photo-grid">' + fRest.map(function (ph) {
              var pid = ph.id ? ' data-photo-id="' + esc(ph.id) + '" tabindex="0" role="button" aria-label="暗房放大检视：' + esc(ph.caption || ph.name || "") + '"' : '';
              return '<figure class="f-photo-item"' + pid + '>' +
                '<img src="' + esc(ph.src) + '" alt="' + esc(ph.caption || ph.name || "") + '" loading="lazy">' +
                (ph.caption ? "<figcaption>" + esc(ph.caption) + "</figcaption>" : "") +
              "</figure>";
            }).join("") + '</div>' +
            (fBig ? '<figure class="f-photo-feature" data-photo-id="' + esc(fBig.id) + '" tabindex="0" role="button" aria-label="暗房放大检视：' + esc(fBig.caption || fBig.name || "") + '">' +
              '<img src="' + esc(fBig.src) + '" alt="' + esc(fBig.caption || fBig.name || "") + '" loading="lazy">' +
              '<figcaption><span class="mono">' + esc(fBig.date || "") + '</span><strong>' + esc(fBig.caption || fBig.name) + '</strong></figcaption>' +
            '</figure>' : '') +
          '</div>';
        } else {
          photosHtml = '<div class="vol-photos-wrap">' +
            '<div class="vol-photos-head">' +
              '<strong>本卷影像锚点 · ' + v.photos.length + ' 帧</strong>' +
              '<span>点击任意合影可暗房放大检视完整比例</span>' +
            '</div>' +
            '<div class="vol-photos">' + v.photos.map(function (ph) {
              var pid = ph.id ? ' data-photo-id="' + esc(ph.id) + '"' : '';
              return '<figure class="photo-frame"' + pid + '>' +
                '<img src="' + esc(ph.src) + '" alt="' + esc(ph.caption || ph.name || "") + '" loading="lazy">' +
                (ph.caption ? "<figcaption>" + esc(ph.caption) + "</figcaption>" : "") +
              "</figure>";
            }).join("") + '</div>' +
          '</div>';
        }
      }

      return '<section class="vol-block" data-badge="' + esc(v.badge) + '">' +
        '<div class="vol-header">' +
          '<div class="vol-title-row">' +
            '<span class="vol-no">' + esc(no) + "</span>" +
            '<span class="' + badgeClass(v.badge) + '">' + esc(v.badge) + "</span>" +
            "<h3>" + esc(v.label) + "</h3>" +
          "</div>" +
          '<span class="mono muted">' + esc(v.period) + " · " + esc(v.title) + "</span>" +
        "</div>" +
        (kws ? '<div class="vol-keywords">' + kws + "</div>" : "") +
        '<div class="event-list">' + evs + "</div>" +
        photosHtml +
      "</section>";
    }).join("");

    $("theme-grid").innerHTML = (D.themes || []).map(function (th, idx) {
      return '<article class="theme-card">' +
        '<span class="theme-roman">DOSSIER · ' + esc(ROMAN[idx] || String(idx + 1)) + "</span>" +
        "<h4>" + esc(th.title) + "</h4>" +
        '<span class="mono">' + esc(th.span) + "</span>" +
        "<p>" + (th.html || "") + "</p>" +
      "</article>";
    }).join("");
  }

  function renderEssays() {
    var list = D.essays || [];
    if (!list.length) return;
    var lead = list[0];
    var rest = list.slice(1);

    if ($("essay-lead")) {
      $("essay-lead").innerHTML =
        '<button type="button" class="lead-card" data-slug="' + esc(lead.slug) + '">' +
          '<div class="lead-top">' +
            '<span class="badge badge-21c">卷首特稿</span>' +
            '<span class="' + badgeClass(lead.badge) + '">' + esc(lead.badge) + "</span>" +
            '<span class="mono muted">' + esc(lead.tag) + "</span>" +
          "</div>" +
          "<h3>" + esc(lead.title) + "</h3>" +
          "<p>" + esc(stripTitlePrefix(lead.excerpt, lead.title)) + "</p>" +
          '<div class="lead-foot mono muted">' +
            "<span>" + esc(lead.date) + " · " + esc(lead.words) + " 字</span>" +
            '<span class="lead-go">展卷阅读 →</span>' +
          "</div>" +
        "</button>";
    }

    $("essay-grid").innerHTML = rest.map(function (e, idx) {
      return '<button type="button" class="essay-card" data-slug="' + esc(e.slug) + '">' +
        '<div class="essay-card-top">' +
          '<span class="' + badgeClass(e.badge) + '">' + esc(e.badge) + "</span>" +
          '<span class="essay-no">' + String(idx + 2).padStart(2, "0") + " · " + esc(e.tag) + "</span>" +
        "</div>" +
        "<h3>" + esc(e.title) + "</h3>" +
        "<p>" + esc(stripTitlePrefix(e.excerpt, e.title)) + "</p>" +
        '<div class="essay-card-foot mono">' +
          "<span>" + esc(e.date) + "</span>" +
          "<span>" + esc(e.words) + " 字</span>" +
        "</div>" +
      "</button>";
    }).join("");
  }

  function renderArchiveStatic() {
    var ar = D.archive || {};
    $("groups-tbody").innerHTML = (ar.groups || []).map(function (g) {
      return "<tr>" +
        "<td><strong>" + esc(g.name) + "</strong></td>" +
        "<td>" + esc(g.role) + "</td>" +
        '<td class="mono">' + esc(g.span) + "</td>" +
        '<td class="num">' + esc(g.messages) + "</td>" +
        '<td class="num">' + esc(g.files) + "</td>" +
      "</tr>";
    }).join("");

    var sems = ar.semesters || [];
    var maxSem = Math.max.apply(null, sems.map(function (s) { return s.files || 0; }).concat([1]));
    $("semester-grid").innerHTML = sems.map(function (s) {
      var pct = Math.max(4, Math.round(((s.files || 0) / maxSem) * 100));
      var isF = (s.stage || "").indexOf("21F班") !== -1;
      return '<div class="sem-card">' +
        '<div class="sem-top">' +
          "<strong>" + esc(s.stage) + "</strong>" +
          '<span class="mono">' + esc(s.files) + " 份</span>" +
        "</div>" +
        '<div class="sem-bar-track" aria-hidden="true">' +
          '<div class="sem-bar-fill' + (isF ? " bar-f" : "") + '" style="width:' + pct + '%"></div>' +
        "</div>" +
        '<p class="sem-summary">' + esc(s.summary) + "</p>" +
        '<p class="sem-groups mono">' + esc(s.groups) + "</p>" +
      "</div>";
    }).join("");

    var cats = ar.categories || [];
    var maxCat = Math.max.apply(null, cats.map(function (c) { return c.total || 0; }).concat([1]));
    $("cat-chips").innerHTML = cats.map(function (c) {
      var clickable = Number(c.code) <= 9 ? "true" : "false";
      var pct = Math.max(4, Math.round(((c.total || 0) / maxCat) * 100));
      return '<button type="button" class="cat-chip" data-code="' + esc(c.code) + '" data-clickable="' + clickable + '">' +
        '<div class="cat-chip-head">' +
          '<span class="cat-chip-title">' + esc(c.code + ". " + c.name) + "</span>" +
          '<span class="mono muted">' + esc(c.total) + " 条</span>" +
        "</div>" +
        '<p class="cat-chip-desc">' + esc(c.summary) + "</p>" +
        '<div class="cat-bar-track" aria-hidden="true"><div class="cat-bar-fill" style="width:' + pct + '%"></div></div>' +
      "</button>";
    }).join("");
  }

  function renderFilesTable() {
    var ar = D.archive || {};
    var cats09 = (ar.categories || []).filter(function (c) { return Number(c.code) <= 9; });
    var tabList = [{ code: "all", name: "全部 01–09" }].concat(cats09);

    $("cat-tabs").innerHTML = tabList.map(function (c) {
      var sel = state.catFilter === c.code ? "true" : "false";
      var label = c.code === "all" ? c.name : c.code + " " + c.name;
      return '<button type="button" class="tab-btn" role="tab" aria-selected="' + sel + '" data-cat="' + esc(c.code) + '">' + esc(label) + "</button>";
    }).join("");

    var q = state.query.trim().toLowerCase();
    var filtered = (ar.files || []).filter(function (f) {
      if (state.catFilter !== "all" && f.cat !== state.catFilter) return false;
      if (!q) return true;
      return (f.filename + " " + f.catName + " " + f.group + " " + f.date).toLowerCase().indexOf(q) !== -1;
    });

    var autoExpand = !!q || state.catFilter !== "all";
    var shown = (autoExpand || state.expandFiles) ? filtered : filtered.slice(0, DEFAULT_FILE_LIMIT);

    $("file-count").textContent = "显示 " + shown.length + " / 共 " + filtered.length + " 条";
    if (autoExpand) {
      $("file-expand").hidden = true;
    } else {
      $("file-expand").hidden = filtered.length <= DEFAULT_FILE_LIMIT;
      $("file-expand").textContent = state.expandFiles ? "收起列表" : "展开全部 (" + filtered.length + ")";
    }

    if (!shown.length) {
      $("files-tbody").innerHTML = '<tr><td colspan="3" class="empty-cell">没有匹配到相关课程文件</td></tr>';
      return;
    }

    $("files-tbody").innerHTML = shown.map(function (f) {
      return "<tr>" +
        '<td class="col-date mono muted">' + esc(f.date) + "</td>" +
        '<td class="fname-cell">' + esc(f.filename) + "</td>" +
        '<td class="col-group muted">' + esc(f.group) + "</td>" +
      "</tr>";
    }).join("");
  }

  function renderVideos() {
    var specs = D.specials || [];
    if ($("special-grid")) {
      $("special-grid").innerHTML = specs.map(function (sp) {
        return '<a class="special-card" href="' + esc(sp.url) + '" target="_blank" rel="noopener noreferrer">' +
          '<div class="special-card-main">' +
            '<div class="special-card-top">' +
              '<span class="seal-tag">' + esc(sp.badge) + "</span>" +
              '<span class="mono">' + esc(sp.date) + "</span>" +
            "</div>" +
            "<h4>" + esc(sp.title) + "</h4>" +
            '<p class="special-card-desc">' + esc(sp.desc) + "</p>" +
            '<p class="special-card-meta mono">' + esc(sp.meta) + "</p>" +
          "</div>" +
          '<span class="special-card-arrow">进入寄语墙特展 ↗</span>' +
        "</a>";
      }).join("");
    }
    var vids = (D.archive && D.archive.videos) || [];
    $("video-grid").innerHTML = vids.map(function (v, idx) {
      return '<a class="video-card" href="' + esc(v.url) + '" target="_blank" rel="noopener noreferrer">' +
        '<div class="video-reel-row">' +
          '<span class="reel-no">REEL ' + String(idx + 1).padStart(2, "0") + "</span>" +
          '<span class="video-bvid">' + esc(v.bvid) + "</span>" +
        "</div>" +
        "<h4>" + esc(v.title) + "</h4>" +
        "<p>" + esc(v.meta) + "</p>" +
      "</a>";
    }).join("");

  }

  function renderClassPhotos() {
    var grid = $("cwall-grid");
    var feat = $("cwall-feature");
    if (!grid || !feat) return;
    var list = (D.photos || []).filter(function (p) { return p.theme === "C班影像"; });
    if (!list.length) return;
    var big = list.filter(function (p) { return (p.name || "").indexOf("毕业合影") >= 0; })[0] || list[list.length - 1];
    var rest = list.filter(function (p) { return p !== big; }).sort(function (a, b) {
      return String(a.date || "").localeCompare(String(b.date || ""));
    });
    grid.innerHTML = rest.map(function (ph) {
      return '<figure class="cwall-item" data-photo-id="' + esc(ph.id) + '" tabindex="0" role="button" aria-label="暗房放大检视：' + esc(ph.caption || ph.name) + '">' +
        '<img src="' + esc(ph.src) + '" alt="' + esc(ph.caption || ph.name) + '" loading="lazy">' +
        '<figcaption><strong>' + esc(ph.caption || ph.name) + '</strong>' +
        '<span class="mono">' + esc(ph.date || "") + '</span></figcaption>' +
      '</figure>';
    }).join("");
    feat.setAttribute("data-photo-id", big.id || "");
    feat.setAttribute("tabindex", "0");
    feat.setAttribute("role", "button");
    feat.setAttribute("aria-label", "暗房放大检视：" + (big.caption || big.name));
    feat.innerHTML = '<img src="' + esc(big.src) + '" alt="' + esc(big.caption || big.name) + '" loading="lazy">' +
      '<figcaption>' +
        '<span class="mono">' + esc(big.date || "") + '</span>' +
        '<strong>' + esc(big.caption || big.name) + '</strong>' +
      '</figcaption>';
  }

  function updateProgress() {
    var el = $("reader");
    var max = el.scrollHeight - el.clientHeight;
    var pct = max > 0 ? Math.min(100, Math.max(0, (el.scrollTop / max) * 100)) : 0;
    $("reader-progress").style.width = pct.toFixed(1) + "%";
  }

  function openEssay(slug, trigger, skipHash) {
    var entry = ESSAY_MAP.get(slug);
    if (!entry) return;
    var e = entry.essay;
    var idx = entry.index;

    if (trigger) state.lastTrigger = trigger;
    state.activeSlug = slug;

    $("reader-badge").className = badgeClass(e.badge);
    $("reader-badge").textContent = e.badge;
    $("reader-bar-tag").textContent = e.tag;
    $("reader-title").textContent = e.title;
    $("reader-meta").innerHTML = [
      "<span>" + esc(e.date) + "</span>",
      "<span>" + esc(e.tag) + "</span>",
      "<span>" + esc(e.words) + " 字</span>"
    ].join("");
    $("reader-body").innerHTML = e.body || "";

    var firstP = $("reader-body").querySelector("p");
    if (firstP) {
      var pText = firstP.textContent || "";
      var tt = String(e.title).replace(/\s+/g, "");
      if (pText.replace(/\s+/g, "") === tt) {
        firstP.remove();
      } else if (stripTitlePrefix(pText, e.title) !== pText) {
        firstP.textContent = stripTitlePrefix(pText, e.title);
      }
    }

    var prev = idx > 0 ? D.essays[idx - 1] : null;
    var next = idx < D.essays.length - 1 ? D.essays[idx + 1] : null;
    $("reader-prev").disabled = !prev;
    $("reader-prev").dataset.slug = prev ? prev.slug : "";
    $("reader-prev").textContent = prev ? "← 上一篇：" + prev.title : "← 已是第一篇";
    $("reader-next").disabled = !next;
    $("reader-next").dataset.slug = next ? next.slug : "";
    $("reader-next").textContent = next ? "下一篇：" + next.title + " →" : "已是最后一篇 →";

    $("reader").hidden = false;
    $("reader").scrollTop = 0;
    document.body.style.overflow = "hidden";
    updateProgress();

    if (!skipHash) {
      var targetHash = "#/essay/" + slug;
      if (location.hash !== targetHash) {
        history.pushState(null, "", targetHash);
      }
    }
    $("reader-close").focus();
  }

  function closeReader(skipHash) {
    if ($("reader").hidden) return;
    $("reader").hidden = true;
    document.body.style.overflow = "";
    state.activeSlug = null;
    if (!skipHash && location.hash.indexOf("#/essay/") === 0) {
      history.replaceState(null, "", "#essays");
    }
    if (state.lastTrigger && state.lastTrigger.focus) {
      state.lastTrigger.focus();
    }
  }

  function syncFromHash() {
    var h = location.hash || "";
    if (h.indexOf("#/essay/") === 0) {
      var slug = decodeURIComponent(h.slice(8));
      if (ESSAY_MAP.has(slug)) {
        openEssay(slug, null, true);
        return;
      }
    }
    if (!$("reader").hidden) {
      closeReader(true);
    }
  }

  // 暗房全屏检视灯箱（支持 12 张 F/C 班照片无裁切检视与键盘翻页）
  var activePhotoIdx = -1;
  var lastPhotoTrigger = null;

  function openLightboxByIndex(idx, trigger) {
    var photos = D.photos || [];
    if (!photos.length || idx < 0 || idx >= photos.length) return;
    var lb = $("lightbox");
    if (!lb) return;
    if (trigger) lastPhotoTrigger = trigger;
    activePhotoIdx = idx;
    var ph = photos[idx];
    $("lightbox-img").src = ph.src;
    $("lightbox-img").alt = ph.caption || ph.name || "";
    $("lightbox-title").textContent = ph.caption || ph.name || "";
    $("lightbox-sub").textContent = (ph.theme || ph.badge || "") + (ph.date ? " · " + ph.date : "");
    $("lightbox-meta").textContent = (ph.badge || "") + " · FRAME " + String(idx + 1).padStart(2, "0") + " / " + String(photos.length).padStart(2, "0");
    $("lightbox-prev").disabled = idx <= 0;
    $("lightbox-next").disabled = idx >= photos.length - 1;
    lb.hidden = false;
    document.body.style.overflow = "hidden";
    $("lightbox-close").focus();
  }

  function openLightbox(photoId, trigger) {
    var photos = D.photos || [];
    for (var i = 0; i < photos.length; i++) {
      if (photos[i].id === photoId) {
        openLightboxByIndex(i, trigger);
        return;
      }
    }
  }

  function closeLightbox() {
    var lb = $("lightbox");
    if (!lb || lb.hidden) return;
    lb.hidden = true;
    document.body.style.overflow = "";
    activePhotoIdx = -1;
    if (lastPhotoTrigger && lastPhotoTrigger.focus) {
      lastPhotoTrigger.focus();
    }
  }

  document.addEventListener("click", function (ev) {
    var fig = ev.target.closest("[data-photo-id]");
    if (fig && fig.dataset.photoId) {
      openLightbox(fig.dataset.photoId, fig);
      return;
    }
    var lb = $("lightbox");
    if (lb && !lb.hidden && ev.target === lb) {
      closeLightbox();
    }
  });

  document.addEventListener("keydown", function (ev) {
    if (ev.key === "Enter" || ev.key === " ") {
      var fig = document.activeElement && document.activeElement.closest ? document.activeElement.closest("[data-photo-id]") : null;
      if (fig && fig.dataset.photoId) {
        ev.preventDefault();
        openLightbox(fig.dataset.photoId, fig);
      }
    }
  });

  if ($("lightbox-close")) {
    $("lightbox-close").addEventListener("click", closeLightbox);
    $("lightbox-prev").addEventListener("click", function () {
      if (activePhotoIdx > 0) openLightboxByIndex(activePhotoIdx - 1, null);
    });
    $("lightbox-next").addEventListener("click", function () {
      var photos = D.photos || [];
      if (activePhotoIdx >= 0 && activePhotoIdx < photos.length - 1) {
        openLightboxByIndex(activePhotoIdx + 1, null);
      }
    });
  }

  var bands = Array.prototype.slice.call(document.querySelectorAll("section[data-band]"));
  var navLinks = Array.prototype.slice.call(document.querySelectorAll(".site-nav a[data-nav]"));
  function syncNav() {
    var mid = Math.max(90, window.innerHeight * 0.32);
    var cur = "";
    var schedEl = $("schedule-container");
    if (schedEl) {
      var sr = schedEl.getBoundingClientRect();
      if (sr.top <= mid && sr.bottom > mid) {
        cur = "schedule";
      }
    }
    if (!cur) {
      for (var i = 0; i < bands.length; i++) {
        var r = bands[i].getBoundingClientRect();
        if (r.top <= mid && r.bottom > mid) {
          cur = bands[i].dataset.band;
          break;
        }
      }
    }
    navLinks.forEach(function (a) {
      if (a.dataset.nav === cur) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
  }
  var navTicking = false;
  window.addEventListener("scroll", function () {
    if (navTicking) return;
    navTicking = true;
    window.requestAnimationFrame(function () {
      syncNav();
      navTicking = false;
    });
  }, { passive: true });

  // Event bindings
  $("vol-tabs").addEventListener("click", function (ev) {
    var btn = ev.target.closest("button[data-vol]");
    if (!btn) return;
    state.volFilter = btn.dataset.vol;
    renderChronicle();
  });

  if ($("essay-lead")) {
    $("essay-lead").addEventListener("click", function (ev) {
      var card = ev.target.closest(".lead-card[data-slug]");
      if (!card) return;
      openEssay(card.dataset.slug, card, false);
    });
  }

  $("essay-grid").addEventListener("click", function (ev) {
    var card = ev.target.closest(".essay-card[data-slug]");
    if (!card) return;
    openEssay(card.dataset.slug, card, false);
  });

  document.querySelectorAll("[data-open-slug]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      openEssay(btn.dataset.openSlug, btn, false);
    });
  });

  $("groups-toggle").addEventListener("click", function () {
    var panel = $("groups-panel");
    var open = panel.hidden;
    panel.hidden = !open;
    $("groups-toggle").setAttribute("aria-expanded", open ? "true" : "false");
    $("groups-toggle-icon").textContent = open ? "− 收起" : "+ 展开";
  });

  $("cat-chips").addEventListener("click", function (ev) {
    var chip = ev.target.closest(".cat-chip[data-clickable='true']");
    if (!chip) return;
    state.catFilter = chip.dataset.code;
    renderFilesTable();
    $("file-search").scrollIntoView({ behavior: "smooth", block: "center" });
  });

  $("cat-tabs").addEventListener("click", function (ev) {
    var btn = ev.target.closest("button[data-cat]");
    if (!btn) return;
    state.catFilter = btn.dataset.cat;
    renderFilesTable();
  });

  $("file-search").addEventListener("input", function () {
    state.query = $("file-search").value;
    renderFilesTable();
  });

  $("file-expand").addEventListener("click", function () {
    state.expandFiles = !state.expandFiles;
    renderFilesTable();
  });

  $("reader").addEventListener("scroll", updateProgress, { passive: true });
  $("reader-close").addEventListener("click", function () { closeReader(false); });

  $("reader-prev").addEventListener("click", function () {
    var slug = $("reader-prev").dataset.slug;
    if (slug) openEssay(slug, null, false);
  });
  $("reader-next").addEventListener("click", function () {
    var slug = $("reader-next").dataset.slug;
    if (slug) openEssay(slug, null, false);
  });

  $("reader-copy").addEventListener("click", function () {
    var btn = $("reader-copy");
    var url = location.href;
    function done() {
      btn.textContent = "已复制";
      setTimeout(function () { btn.textContent = "复制链接"; }, 1500);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(done, done);
    } else {
      var ta = document.createElement("textarea");
      ta.value = url;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand("copy"); } catch (err) {}
      document.body.removeChild(ta);
      done();
    }
  });

  document.addEventListener("keydown", function (ev) {
    var lb = $("lightbox");
    if (lb && !lb.hidden) {
      if (ev.key === "Escape") {
        closeLightbox();
      } else if (ev.key === "ArrowLeft" && activePhotoIdx > 0) {
        openLightboxByIndex(activePhotoIdx - 1, null);
      } else if (ev.key === "ArrowRight" && activePhotoIdx < (D.photos || []).length - 1) {
        openLightboxByIndex(activePhotoIdx + 1, null);
      }
      return;
    }
    if ($("reader").hidden) return;
    var activeTag = document.activeElement ? document.activeElement.tagName : "";
    if (ev.key === "Escape") {
      closeReader(false);
    } else if (activeTag !== "INPUT" && activeTag !== "TEXTAREA") {
      if (ev.key === "ArrowLeft" && !$("reader-prev").disabled) {
        openEssay($("reader-prev").dataset.slug, null, false);
      } else if (ev.key === "ArrowRight" && !$("reader-next").disabled) {
        openEssay($("reader-next").dataset.slug, null, false);
      }
    }
  });

  window.addEventListener("hashchange", syncFromHash);

  renderHeroStats();
  renderChronicle();
  renderEssays();
  renderArchiveStatic();
  renderFilesTable();
  renderClassPhotos();
  renderVideos();
  syncFromHash();
  syncNav();
})();

// 深链接兜底：内容由脚本渲染，hash 目标可能在初始解析时尚不存在
window.addEventListener("load", function () {
  if (!location.hash) return;
  setTimeout(function () {
    try {
      var el = document.querySelector(location.hash);
      if (el) el.scrollIntoView({ block: "start" });
    } catch (e) {}
  }, 120);
});
