document.addEventListener("DOMContentLoaded", function () {
  var root = document.getElementById("schedule-container");
  var app = document.getElementById("notice-app");
  var payload = window.COURSE_NOTICES;
  if (!root || !app || !payload || !payload.entries) return;

  var meta = payload.meta || {};
  var entries = payload.entries.slice().sort(function (a, b) {
    return a.timestamp < b.timestamp ? -1 : a.timestamp > b.timestamp ? 1 : 0;
  });
  var state = { group: "all", month: "2021-10", date: "2021-10-25" };
  var WEEKDAYS = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"];
  var MONTH_CN = ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"];

  function pad(n) { return n < 10 ? "0" + n : String(n); }
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
  function normalizePlain(s) {
    return String(s == null ? "" : s).replace(/[^\u4e00-\u9fffA-Za-z0-9]/g, "");
  }
  function titleMentionsDate(title, isoDate) {
    if (!isoDate) return false;
    var p = dateParts(isoDate);
    var forms = [p.m + "月" + p.d + "日", pad(p.m) + "月" + pad(p.d) + "日"];
    return forms.some(function (form) { return String(title).indexOf(form) >= 0; });
  }
  function stripRepeatedHead(text, title) {
    var body = String(text == null ? "" : text).replace(/\r/g, "");
    var lines = body.split("\n");
    if (lines.length > 1 && normalizePlain(lines[0]) === normalizePlain(title)) {
      body = lines.slice(1).join("\n").replace(/^\n+/, "").trim();
    }
    return body;
  }
  function displayTitle(e) {
    var title = String(e.title == null ? "" : e.title).replace(/\s+/g, " ").trim();
    var body = String(e.body == null ? "" : e.body);
    var quoted = /^\[?引用/.test(title);
    if (/^\[?链接\/卡片:/.test(title)) {
      title = title.replace(/^\[?链接\/卡片:\s*/, "").replace(/\]\s*$/, "").trim();
    }
    if (quoted) {
      var m = body.match(/↳svrid:\d+\s+([^\n]+)/);
      if (m) {
        title = m[1];
      } else {
        var q = body.match(/^\[引用[^\]]*\]\s*([^\n]+)/);
        if (q) title = q[1];
      }
    }
    title = title.replace(/@所有人\s*/g, "")
      .replace(/^[\p{Extended_Pictographic}\uFE0F\s]+/u, "").trim();
    if (/^以下是考试时间安排/.test(title)) title = "F 班期末考试安排";
    if (/以下是早读内容/.test(title)) title = "早读内容";
    if (title === "一则调课通知∶" && /古代文学二/.test(body)) title = "古代文学二改网课";
    if (title === "会议号来咯") title = "腾讯会议号";
    if (title === "改成腾讯会议啦") title = "古代文学改为腾讯会议";
    if (/^接凌老师通知/.test(title) && /应用写作/.test(body)) title = "应用写作课带电脑提醒";
    if (title === "【考试通知】" && /军事理论/.test(body)) title = "《军事理论》期末测验";
    if (title === "考试时间☀") title = "考试时间安排";
    if (title === "现代汉语") title = "现代汉语期末考试";
    if (title === "文学概论") title = "文学概论期末考试";
    if (title === "【调课通知】" && /古代汉语|古汉语/.test(body)) title = "古代汉语调课通知";
    if (title === "【上课通知】" && /形势与政策/.test(body)) title = "形势与政策上课通知";
    if (title === "【现代教育技术测验】" && /教育学测验/.test(body)) title = "教育学与现代教育技术测验";
    if (title === "Tips" && /洼地上的战役/.test(body)) title = "《洼地上的战役》阅读提醒";
    if (title === "【调课通知】" && /十五周周一/.test(body)) title = "古代文学调至十五周周一";
    if (quoted && /见习安排/.test(body)) title = "本周见习安排";
    if (quoted && /古代汉语/.test(body) && /(调课|调到|调至|改到)/.test(body)) title = "古代汉语调课通知";
    return title || e.title;
  }
  function monthOf(dateStr) { return dateStr.slice(0, 7); }
  function dateParts(dateStr) {
    var parts = dateStr.split("-").map(Number);
    return { y: parts[0], m: parts[1], d: parts[2] };
  }
  function shortDate(dateStr) {
    var p = dateParts(dateStr);
    return p.m + "月" + p.d + "日";
  }
  function weekdayOf(dateStr) {
    var p = dateParts(dateStr);
    return WEEKDAYS[new Date(p.y, p.m - 1, p.d).getDay()];
  }
  function termFor(key) {
    var p = dateParts(key + "-01");
    if (p.y === 2021 && p.m >= 10) return "大一上";
    if (p.y === 2022 && p.m === 1) return "大一上";
    if (p.y === 2022 && p.m >= 2 && p.m <= 7) return "大一下";
    if (p.y === 2022 && p.m === 8) return "暑假";
    if (p.y === 2022 && p.m >= 9) return "大二上";
    if (p.y === 2023 && p.m === 1) return "大二上";
    if (p.y === 2023 && p.m >= 2 && p.m <= 7) return "大二下";
    return "";
  }
  function monthLabel(key) {
    var p = dateParts(key + "-01");
    return p.y + " / " + pad(p.m);
  }
  function monthLongLabel(key) {
    var p = dateParts(key + "-01");
    return p.y + " 年 " + p.m + " 月";
  }
  function matchesGroup(entry) {
    return state.group === "all" || entry.group === state.group;
  }
  function visibleEntries() {
    return entries.filter(matchesGroup);
  }
  function monthList() {
    var map = {};
    visibleEntries().forEach(function (e) {
      var key = monthOf(e.date);
      if (!map[key]) map[key] = { key: key, count: 0, first: e.date };
      map[key].count += 1;
      if (e.date < map[key].first) map[key].first = e.date;
    });
    return Object.keys(map).map(function (key) {
      return { key: key, count: map[key].count, first: map[key].first, term: termFor(key) };
    }).sort(function (a, b) { return a.key < b.key ? -1 : 1; });
  }
  function firstDateInMonth(key) {
    var list = visibleEntries().filter(function (e) { return monthOf(e.date) === key; });
    return list.length ? list[0].date : null;
  }
  function ensureState() {
    var months = monthList();
    if (!months.length) return;
    if (!months.some(function (m) { return m.key === state.month; })) {
      state.month = months[0].key;
      state.date = months[0].first;
    }
    if (!state.date || monthOf(state.date) !== state.month ||
        !visibleEntries().some(function (e) { return e.date === state.date; })) {
      state.date = firstDateInMonth(state.month) || months[0].first;
    }
  }

  function renderTabs() {
    var tabs = [
      { key: "all", label: "全部", count: meta.total || entries.length },
      { key: "F", label: "21F", count: meta.groups ? meta.groups.F : 0 },
      { key: "C", label: "21C", count: meta.groups ? meta.groups.C : 0 }
    ];
    return '<div class="filter-tabs notice-tabs" role="tablist" aria-label="学习群筛选">' +
      tabs.map(function (t) {
        return '<button type="button" class="tab-btn" role="tab" data-notice-group="' + t.key +
          '" aria-selected="' + (state.group === t.key) + '">' + t.label +
          '<span class="notice-tab-count">' + t.count + '</span></button>';
      }).join("") + "</div>";
  }

  function renderMonthNav(months, currentIndex) {
    return '<div class="notice-month-nav">' +
      '<button type="button" class="notice-arrow" data-month-dir="-1" aria-label="上一个月"' +
        (currentIndex <= 0 ? " disabled" : "") + ">←</button>" +
      '<span class="notice-month-select-wrap"><select id="notice-month-select" class="notice-month-select" aria-label="选择月份">' +
        months.map(function (m) {
          return '<option value="' + m.key + '"' + (m.key === state.month ? " selected" : "") + ">" +
            monthLabel(m.key) + "</option>";
        }).join("") +
      '</select><span class="notice-select-caret" aria-hidden="true">▾</span></span>' +
      '<button type="button" class="notice-arrow" data-month-dir="1" aria-label="下一个月"' +
        (currentIndex >= months.length - 1 ? " disabled" : "") + ">→</button>" +
    "</div>";
  }

  function renderCalendar(monthKey) {
    var p = dateParts(monthKey + "-01");
    var firstDay = new Date(p.y, p.m - 1, 1);
    var offset = (firstDay.getDay() + 6) % 7; // 周一为第一列
    var days = new Date(p.y, p.m, 0).getDate();
    var dayEntries = {};
    visibleEntries().forEach(function (e) {
      if (monthOf(e.date) !== monthKey) return;
      if (!dayEntries[e.date]) dayEntries[e.date] = [];
      dayEntries[e.date].push(e);
    });

    var cells = "";
    for (var i = 0; i < offset; i++) {
      cells += '<div class="notice-cell is-blank" aria-hidden="true"></div>';
    }
    for (var d = 1; d <= days; d++) {
      var dateKey = p.y + "-" + pad(p.m) + "-" + pad(d);
      var list = dayEntries[dateKey] || [];
      if (!list.length) {
        cells += '<div class="notice-cell is-empty"><span class="notice-daynum">' + d + "</span></div>";
        continue;
      }
      var fCount = list.filter(function (e) { return e.group === "F"; }).length;
      var cCount = list.filter(function (e) { return e.group === "C"; }).length;
      var selected = dateKey === state.date;
      var marks = "";
      if (fCount) marks += '<span class="notice-mark f" title="21F ' + fCount + ' 条"></span>';
      if (cCount) marks += '<span class="notice-mark c" title="21C ' + cCount + ' 条"></span>';
      var aria = shortDate(dateKey) + "，" + list.length + " 条课讯" +
        (fCount ? "，21F " + fCount + " 条" : "") +
        (cCount ? "，21C " + cCount + " 条" : "");
      cells += '<button type="button" class="notice-cell has-notes' + (selected ? " is-selected" : "") +
        '" data-date="' + dateKey + '" aria-label="' + aria + '" aria-pressed="' + selected + '">' +
        '<span class="notice-daynum">' + d + "</span>" +
        '<span class="notice-marks">' + marks + "</span>" +
        '<span class="notice-daycount">' + list.length + "</span>" +
      "</button>";
    }

    var fMonth = 0, cMonth = 0;
    Object.keys(dayEntries).forEach(function (key) {
      dayEntries[key].forEach(function (e) {
        if (e.group === "F") fMonth += 1; else cMonth += 1;
      });
    });
    var monthTotal = fMonth + cMonth;
    var summary;
    if (state.group === "F") {
      summary = "21F " + fMonth;
    } else if (state.group === "C") {
      summary = "21C " + cMonth;
    } else {
      var parts = [];
      if (fMonth) parts.push("21F " + fMonth);
      if (cMonth) parts.push("21C " + cMonth);
      summary = parts.join(" / ") || "暂无";
    }
    var term = termFor(monthKey);
    var monthName = MONTH_CN[p.m - 1] || (p.m + "月");

    return '<div class="notice-calendar">' +
      '<div class="notice-calendar-summary">' +
        '<div class="notice-month-display"><span class="notice-month-year">' + p.y +
          '</span><span class="notice-month-cn">' + monthName + "</span></div>" +
        '<div class="notice-month-detail">' +
          (term ? "<span>" + term + "</span>" : "") +
          "<span>本月 <strong>" + monthTotal + "</strong> 条</span>" +
          '<span class="notice-month-groups">' + summary + "</span>" +
        "</div>" +
      "</div>" +
      '<div class="notice-weekdays" aria-hidden="true"><span>一</span><span>二</span><span>三</span><span>四</span><span>五</span><span>六</span><span>日</span></div>' +
      '<div class="notice-grid">' + cells + "</div>" +
    "</div>";
  }

  function renderDayPanel() {
    var list = visibleEntries().filter(function (e) { return e.date === state.date; });
    var p = dateParts(state.date);
    var head = '<div class="notice-day-head"><div>' +
      '<div class="notice-day-kicker mono">' + p.y + " / " + pad(p.m) + " / " + pad(p.d) + " · " + weekdayOf(state.date) + "</div>" +
      "<h4>" + p.m + "月" + p.d + "日</h4></div>" +
      '<span class="notice-day-count">' + list.length + " 条</span></div>";

    if (!list.length) {
      return '<div class="notice-day-panel">' + head +
        '<p class="notice-empty">这一天没有留下课讯。</p></div>';
    }

    var cards = list.map(function (e) {
      var badge = e.prelude ? "21F 前史" : e.group === "F" ? "21F" : "21C";
      var cls = "notice-card is-" + e.group.toLowerCase() + (e.prelude ? " is-prelude" : "");
      var classChip = e.classDate && e.classDate !== e.date && !titleMentionsDate(e.title, e.classDate)
        ? '<span class="notice-classdate">对应 ' + shortDate(e.classDate) + "</span>" : "";
      var m = dateParts(e.date);
      var displayBody = stripRepeatedHead(e.body, e.title);
      var titleOnly = normalizePlain(displayBody) === normalizePlain(e.title);
      var bodyHtml = titleOnly ? "" :
        '<div class="notice-body">' + esc(displayBody) + "</div>";
      var moreHtml = titleOnly ? "" :
        '<button type="button" class="notice-more" aria-expanded="false">展开原文 <span aria-hidden="true">↓</span></button>';
      return '<article class="' + cls + '">' +
        '<div class="notice-card-top">' +
          '<span class="notice-badge ' + e.group.toLowerCase() + '">' + badge + "</span>" +
          '<span class="notice-tag">' + esc(e.tag) + "</span>" +
          classChip +
          '<time class="notice-time" datetime="' + e.timestamp.replace(" ", "T") + '">' +
            m.m + "-" + pad(m.d) + " " + esc(e.time) + " 发布</time>" +
        "</div>" +
        '<h4 class="notice-title">' + esc(displayTitle(e)) + "</h4>" +
        bodyHtml +
        '<div class="notice-card-foot">' +
          moreHtml +
          '<span class="notice-section-name">' + esc(e.category) + "</span>" +
        "</div>" +
      "</article>";
    }).join("");

    return '<div class="notice-day-panel">' + head +
      '<div class="notice-list">' + cards + "</div></div>";
  }

  function render() {
    ensureState();
    var months = monthList();
    var currentIndex = months.findIndex(function (m) { return m.key === state.month; });
    if (currentIndex < 0) currentIndex = 0;
    app.innerHTML =
      '<div class="notice-controls">' + renderTabs() +
        renderMonthNav(months, currentIndex) +
      "</div>" +
      renderCalendar(state.month) +
      renderDayPanel();

    var metaEl = document.getElementById("notice-meta");
    if (metaEl && meta.firstDate && meta.lastDate) {
      var range = meta.firstDate.slice(0, 7).replace("-", ".") + "—" +
        meta.lastDate.slice(0, 7).replace("-", ".");
      metaEl.innerHTML = "<span>" + range + "</span><span>" + meta.total + " 条</span>";
    }
    var totalEl = document.getElementById("notice-total");
    if (totalEl && meta.total) totalEl.textContent = meta.total;

    requestAnimationFrame(function () {
      app.querySelectorAll(".notice-body").forEach(function (body) {
        var card = body.closest(".notice-card");
        var btn = card && card.querySelector(".notice-more");
        if (btn && body.scrollHeight <= body.clientHeight + 4) {
          btn.classList.add("is-hidden");
        }
      });
    });
  }

  app.addEventListener("click", function (event) {
    var tab = event.target.closest("[data-notice-group]");
    if (tab) {
      state.group = tab.getAttribute("data-notice-group");
      ensureState();
      render();
      return;
    }
    var arrow = event.target.closest("[data-month-dir]");
    if (arrow && !arrow.disabled) {
      var months = monthList();
      var index = months.findIndex(function (m) { return m.key === state.month; });
      var next = index + Number(arrow.getAttribute("data-month-dir"));
      if (next >= 0 && next < months.length) {
        state.month = months[next].key;
        state.date = months[next].first;
        render();
      }
      return;
    }
    var cell = event.target.closest(".notice-cell.has-notes");
    if (cell) {
      state.date = cell.getAttribute("data-date");
      render();
      return;
    }
    var more = event.target.closest(".notice-more");
    if (more) {
      var card = more.closest(".notice-card");
      if (!card) return;
      var open = card.classList.toggle("is-open");
      more.setAttribute("aria-expanded", String(open));
      more.innerHTML = open ? '收起原文 <span aria-hidden="true">↑</span>' :
        '展开原文 <span aria-hidden="true">↓</span>';
    }
  });

  app.addEventListener("change", function (event) {
    if (event.target.id !== "notice-month-select") return;
    state.month = event.target.value;
    state.date = firstDateInMonth(state.month);
    render();
  });

  render();
});
