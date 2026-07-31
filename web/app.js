/* ParguszPhysics — arayüz mantığı */
(function () {
"use strict";

// ─────────────────────────────────────────── durum
var LANG = localStorage.getItem("pp_lang") || "tr";
var SESSION = localStorage.getItem("pp_session") || ("s" + Date.now());
localStorage.setItem("pp_session", SESSION);
var busy = false;
// Yazma efekti — varsayılan açık, kullanıcı kapatabilir
var TYPING = localStorage.getItem("pp_typing") !== "0";
var UI_SURUM = "1.3";

// ─────────────────────────────────────────── sunucu adresi
// Arayüz GitHub Pages'ten sunulabilir; motor ise kullanıcının kendi
// bilgisayarında çalışır. O yüzden API adresi ayarlanabilir olmalı.
// Aynı adresten sunuluyorsa (yerel kullanım) hiçbir ayar gerekmez.
var SUNUCU = {
  adres: localStorage.getItem("pp_api") || "",
  anahtar: localStorage.getItem("pp_anahtar") || "",

  yerelMi: function () {
    // file:// ya da github.io gibi bir yerden açıldıysa uzak sunucu şart
    var h = location.hostname;
    return h === "localhost" || h === "127.0.0.1" || h === "";
  },

  taban: function () {
    if (this.adres) return this.adres.replace(/\/+$/, "");
    return "";           // aynı köken: /api/... göreli çalışır
  },

  kur: function (adres, anahtar) {
    this.adres = (adres || "").trim().replace(/\/+$/, "");
    this.anahtar = (anahtar || "").trim();
    localStorage.setItem("pp_api", this.adres);
    localStorage.setItem("pp_anahtar", this.anahtar);
  },

  gerekliMi: function () {
    // Sayfa uzak bir alandan geldiyse ve adres ayarlanmadıysa
    return !this.yerelMi() && !this.adres;
  }
};

// Tüm API çağrıları buradan geçer: adres öneki ve anahtar başlığı
// tek yerde eklenir.
function api(yol, secenekler) {
  secenekler = secenekler || {};
  var basliklar = secenekler.headers || {};
  if (SUNUCU.anahtar) basliklar["X-Pargusz-Anahtar"] = SUNUCU.anahtar;
  secenekler.headers = basliklar;
  return fetch(SUNUCU.taban() + yol, secenekler);
}

var $ = function (id) { return document.getElementById(id); };
var chat = $("chat"), input = $("input"), sendBtn = $("send");

// ─────────────────────────────────────────── çeviriler
var I18N = {
  tr: {
    tagline: "Fizik · Hesaplama · MATLAB",
    newChat: "Yeni sohbet", learning: "Öğrenme motoru",
    papers: "makale", concepts: "kavram", links: "bağlantı", terms: "terim",
    stop: "Durdur", start: "Başlat", log: "Kayıt",
    core: "Çekirdek bilgi", topicsL: "konu anlatımı",
    formulasL: "çözülebilir formül", constL: "fiziksel sabit",
    langHint: "Konuşma dili. Makaleler her dilden taranır.",
    heroSub: "Fizik hesaplamaları, konu anlatımı, formül çözümü, MATLAB kodu ve canlı literatür taraması.",
    placeholder: "Bir fizik sorusu sorun, formül yazın veya hesaplama isteyin…",
    foot: "Enter ile gönder · Shift+Enter yeni satır",
    you: "Sen", bot: "ParguszPhysics", copy: "kopyala", copied: "kopyalandı",
    typing: "Yazma efekti", on: "açık", off: "kapalı",
    history: "Sohbetler", noHistory: "Henüz sohbet yok",
    clearAll: "Tümünü sil",
    clearAllAsk: "Tüm sohbet geçmişi silinsin mi?\n\n" +
      "Yalnızca konuşma dökümü gider. Sistemin bu sohbetlerden " +
      "öğrendiği bilgiler (makaleler, kavramlar, formüller) yerinde kalır.",
    clearAllDone: "sohbet silindi",
    untitled: "Adsız sohbet", del: "Sil",
    attach: "Dosya ekle", reading: "Belge okunuyor…",
    insights: "bulgu", docs: "belge",
    llm: "Dil modeli", llmNone: "kurulu değil — kural tabanlı",
    llmReady: "hazır", llmLoaded: "bellekte",
    uploadErr: "Dosya yüklenemedi.", tooBig: "Dosya çok büyük (en fazla 60 MB).",
    err: "Sunucuya ulaşılamadı. Terminal penceresinin açık olduğundan emin olun."
  },
  en: {
    tagline: "Physics · Computation · MATLAB",
    newChat: "New chat", learning: "Learning engine",
    papers: "papers", concepts: "concepts", links: "links", terms: "terms",
    stop: "Stop", start: "Start", log: "Log",
    core: "Core knowledge", topicsL: "topic explanations",
    formulasL: "solvable formulas", constL: "physical constants",
    langHint: "Conversation language. Papers are scanned in every language.",
    heroSub: "Physics calculations, topic explanations, formula solving, MATLAB code and live literature search.",
    placeholder: "Ask a physics question, write a formula or request a calculation…",
    foot: "Enter to send · Shift+Enter for a new line",
    you: "You", bot: "ParguszPhysics", copy: "copy", copied: "copied",
    typing: "Typing effect", on: "on", off: "off",
    history: "Chats", noHistory: "No chats yet",
    clearAll: "Delete all",
    clearAllAsk: "Delete the entire chat history?\n\n" +
      "Only the transcript is removed. What the system learned from " +
      "these chats stays.",
    clearAllDone: "chats deleted",
    untitled: "Untitled chat", del: "Delete",
    attach: "Attach a file", reading: "Reading document…",
    insights: "insights", docs: "docs",
    llm: "Language model", llmNone: "not installed — rule-based",
    llmReady: "ready", llmLoaded: "loaded",
    uploadErr: "Upload failed.", tooBig: "File too large (max 60 MB).",
    err: "Could not reach the server. Make sure the terminal window is still open."
  }
};
function t(k) { return (I18N[LANG] && I18N[LANG][k]) || I18N.tr[k] || k; }

function applyLang() {
  document.documentElement.lang = LANG;
  document.querySelectorAll("[data-i18n]").forEach(function (el) {
    el.textContent = t(el.getAttribute("data-i18n"));
  });
  document.querySelectorAll("[data-i18n-ph]").forEach(function (el) {
    el.placeholder = t(el.getAttribute("data-i18n-ph"));
  });
  document.querySelectorAll(".lang").forEach(function (b) {
    b.classList.toggle("active", b.dataset.lang === LANG);
  });
  var te = $("toggleEngine");
  if (te) te.textContent = te.dataset.running === "1" ? t("stop") : t("start");
  var tt = $("typingToggle");
  if (tt) {
    tt.textContent = t("typing") + ": " + (TYPING ? t("on") : t("off"));
    tt.setAttribute("aria-pressed", TYPING ? "true" : "false");
    tt.classList.toggle("on", TYPING);
  }
  var ab = $("attachBtn");
  if (ab) ab.title = t("attach");
  loadSuggestions();
}

// ─────────────────────────────────────────── markdown
function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;")
                  .replace(/>/g, "&gt;");
}

var MATLAB_KEYS = /\b(function|end|for|while|if|elseif|else|switch|case|otherwise|return|break|continue|clear|clc|close|figure|hold|grid|subplot|plot|semilogx|semilogy|loglog|xlabel|ylabel|title|legend|axis|fprintf|disp|linspace|logspace|zeros|ones|eye|size|numel|length|sum|mean|max|min|sort|find|abs|sqrt|exp|log|sin|cos|tan|ode45|ode15s|fft|ifft|polyfit|polyval|fminsearch|odeset|optimset|deg2rad|rad2deg|randn|rand|trapz|diag|eig|inv|norm|mod|round|histogram|errorbar|quiver|contourf|colormap|colorbar|drawnow|xline|yline|stem|set|syms|diff|int|dsolve|solve|simplify|ismember|mode|sign|nan|NaN|inf|Inf|pi|true|false)\b/g;

// Kod parçalarını (yorum/dize dışındaki bölümleri) vurgula
function highlightCodeSpan(s) {
  s = esc(s);
  s = s.replace(MATLAB_KEYS, '<span class="tok-key">$1</span>');
  s = s.replace(/\b(\d+\.?\d*(?:[eE][-+]?\d+)?)\b/g,
                '<span class="tok-num">$1</span>');
  return s;
}

function highlightMatlab(code) {
  // Yorumlar ve dizeler ayrı ayrı işlenir; aralarında kalan gerçek kod
  // parçalarına anahtar kelime/sayı vurgulaması uygulanır. Yer tutucu
  // kullanılmaz — yer tutucu yaklaşımı, sayı vurgulaması yer tutucuyu
  // yuttuğu için yorumları "0", "1", "2" diye gösteriyordu.
  var re = /(%[^\n]*)|('(?:[^'\n]|'')*')/g;
  var out = "", last = 0, m;
  while ((m = re.exec(code)) !== null) {
    out += highlightCodeSpan(code.slice(last, m.index));
    var raw = m[0];
    var cls = raw.charAt(0) === "%" ? "tok-com" : "tok-str";
    out += '<span class="' + cls + '">' + esc(raw) + "</span>";
    last = re.lastIndex;
  }
  out += highlightCodeSpan(code.slice(last));
  return out;
}

function inline(s) {
  s = esc(s);
  // kod
  s = s.replace(/`([^`]+)`/g, function (_, c) { return "<code>" + c + "</code>"; });
  // bağlantı
  s = s.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g,
    '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
  // kalın / italik
  s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  s = s.replace(/(^|[^*\w])\*([^*\n]+)\*(?![*\w])/g, "$1<em>$2</em>");
  s = s.replace(/(^|\s)_([^_\n]+)_(?=\s|$|[.,;:!?])/g, "$1<em>$2</em>");
  // izin verilen span
  s = s.replace(/&lt;span class=&#39;meta&#39;&gt;/g, "<span class='meta'>")
       .replace(/&lt;span class='meta'&gt;/g, "<span class='meta'>")
       .replace(/&lt;\/span&gt;/g, "</span>");
  return s;
}

function markdown(src) {
  var lines = String(src || "").replace(/\r/g, "").split("\n");
  var out = [], i = 0;

  while (i < lines.length) {
    var line = lines[i];

    // kod bloğu
    var fence = line.match(/^```(\w*)\s*$/);
    if (fence) {
      var lang = fence[1] || "", buf = [];
      i++;
      while (i < lines.length && !/^```\s*$/.test(lines[i])) { buf.push(lines[i]); i++; }
      i++;
      var raw = buf.join("\n");
      var html = /matlab|octave|m/i.test(lang) ? highlightMatlab(raw) : esc(raw);
      out.push('<pre><button class="copy-btn" data-code="' +
               encodeURIComponent(raw) + '">' + t("copy") + "</button><code>" +
               html + "</code></pre>");
      continue;
    }

    // başlık
    var h = line.match(/^(#{1,4})\s+(.*)$/);
    if (h) {
      var lvl = Math.min(h[1].length, 3);
      out.push("<h" + lvl + ">" + inline(h[2]) + "</h" + lvl + ">");
      i++; continue;
    }

    // yatay çizgi
    if (/^\s*---+\s*$/.test(line)) { out.push("<hr>"); i++; continue; }

    // tablo
    if (/\|/.test(line) && i + 1 < lines.length && /^\s*\|?[\s:|-]+\|[\s:|-]*$/.test(lines[i + 1])) {
      var head = line, rows = [];
      i += 2;
      while (i < lines.length && /\|/.test(lines[i]) && lines[i].trim()) {
        rows.push(lines[i]); i++;
      }
      var cells = function (r) {
        return r.replace(/^\s*\|/, "").replace(/\|\s*$/, "").split("|")
                .map(function (c) { return c.trim(); });
      };
      var th = cells(head).map(function (c) { return "<th>" + inline(c) + "</th>"; }).join("");
      var tb = rows.map(function (r) {
        return "<tr>" + cells(r).map(function (c) {
          return "<td>" + inline(c) + "</td>";
        }).join("") + "</tr>";
      }).join("");
      out.push("<table><thead><tr>" + th + "</tr></thead><tbody>" + tb + "</tbody></table>");
      continue;
    }

    // alıntı
    if (/^\s*>\s?/.test(line)) {
      var q = [];
      while (i < lines.length && /^\s*>\s?/.test(lines[i])) {
        q.push(lines[i].replace(/^\s*>\s?/, "")); i++;
      }
      out.push("<blockquote>" + markdown(q.join("\n")) + "</blockquote>");
      continue;
    }

    // liste
    if (/^\s*([-*+]|\d+\.)\s+/.test(line)) {
      var ordered = /^\s*\d+\./.test(line);
      var items = [];
      while (i < lines.length && /^\s*([-*+]|\d+\.)\s+/.test(lines[i])) {
        var txt = lines[i].replace(/^\s*([-*+]|\d+\.)\s+/, "");
        i++;
        // devam eden girintili satırlar
        while (i < lines.length && /^\s{2,}\S/.test(lines[i]) &&
               !/^\s*([-*+]|\d+\.)\s+/.test(lines[i])) {
          txt += " " + lines[i].trim(); i++;
        }
        items.push("<li>" + inline(txt) + "</li>");
      }
      out.push((ordered ? "<ol>" : "<ul>") + items.join("") +
               (ordered ? "</ol>" : "</ul>"));
      continue;
    }

    // boş satır
    if (!line.trim()) { i++; continue; }

    // paragraf
    var p = [];
    while (i < lines.length && lines[i].trim() &&
           !/^```/.test(lines[i]) && !/^#{1,4}\s/.test(lines[i]) &&
           !/^\s*([-*+]|\d+\.)\s+/.test(lines[i]) && !/^\s*>/.test(lines[i]) &&
           !/^\s*---+\s*$/.test(lines[i])) {
      p.push(lines[i]); i++;
    }
    if (p.length) out.push("<p>" + inline(p.join("\n")).replace(/\n/g, "<br>") + "</p>");
  }
  return out.join("\n");
}

// ─────────────────────────────────────────── yazma efekti
// Cevap sunucudan tek parça gelir; burada kademeli olarak açılır.
// Markdown yeniden ayrıştırılmaz: son HTML bir kez kurulur, sonra metin
// düğümleri sırayla doldurulur. Böylece kod vurgulaması, tablolar ve
// bağlantılar yazma sırasında bozulmaz.

var TYPE_CPS_MS = 1.1;    // ~900 karakter/saniye
var TYPE_MIN_MS = 350;
var TYPE_MAX_MS = 3200;
var typer = null;         // yürüyen yazma işlemi

function collectTextNodes(root) {
  var out = [];
  var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false);
  var n;
  while ((n = w.nextNode())) {
    var p = n.parentNode;
    if (p && p.classList && p.classList.contains("copy-btn")) continue;
    if (n.nodeValue && n.nodeValue.length) out.push(n);
  }
  return out;
}

function typeInto(el, html, onDone) {
  el.innerHTML = html;
  var blocks = Array.prototype.slice.call(el.children);
  var nodes = collectTextNodes(el);
  var full = nodes.map(function (n) { return n.nodeValue; });
  var total = full.reduce(function (a, s) { return a + s.length; }, 0);

  var copies = Array.prototype.slice.call(el.querySelectorAll(".copy-btn"));

  var failsafe = 0;

  function finish() {
    if (failsafe) { clearTimeout(failsafe); failsafe = 0; }
    for (var k = 0; k < nodes.length; k++) nodes[k].nodeValue = full[k];
    blocks.forEach(function (b) { b.classList.remove("pending"); });
    if (caret.parentNode) caret.parentNode.removeChild(caret);
    copies.forEach(function (b) { b.style.visibility = ""; });
    if (typer === handle) typer = null;
    if (onDone) onDone();
  }

  var handle = { finish: finish };
  if (!total) { finish(); return handle; }

  nodes.forEach(function (n) { n.nodeValue = ""; });
  blocks.forEach(function (b) { b.classList.add("pending"); });
  copies.forEach(function (b) { b.style.visibility = "hidden"; });

  var caret = document.createElement("span");
  caret.className = "caret";

  var dur = Math.min(TYPE_MAX_MS, Math.max(TYPE_MIN_MS, total * TYPE_CPS_MS));
  var perMs = total / dur;

  var i = 0, pos = 0, acc = 0, last = 0;

  function topBlockOf(node) {
    var p = node.parentNode;
    while (p && p.parentNode !== el) p = p.parentNode;
    return p && p.parentNode === el ? p : null;
  }

  function step(now) {
    if (typer !== handle) return;          // araya girildi
    if (!last) last = now;
    acc += Math.min(now - last, 120) * perMs;
    last = now;
    var budget = Math.floor(acc);
    if (budget > 0) {
      acc -= budget;
      // Kullanıcı yukarı kaydırdıysa onu aşağı sürüklemeyelim
      var nearBottom =
        (chat.scrollHeight - chat.scrollTop - chat.clientHeight) < 140;
      var current = null;
      while (budget > 0 && i < nodes.length) {
        var b = topBlockOf(nodes[i]);
        if (b) { b.classList.remove("pending"); current = b; }
        var take = Math.min(budget, full[i].length - pos);
        pos += take;
        budget -= take;
        nodes[i].nodeValue = full[i].slice(0, pos);
        if (pos >= full[i].length) { i++; pos = 0; }
      }
      if (current && caret.parentNode !== current) current.appendChild(caret);
      if (nearBottom) chat.scrollTop = chat.scrollHeight;
    }
    if (i >= nodes.length) { finish(); return; }
    requestAnimationFrame(step);
  }

  typer = handle;
  requestAnimationFrame(step);
  // Emniyet: requestAnimationFrame arka plan sekmelerinde durdurulur. Bu
  // olmazsa cevap, kullanıcı sekmeye dönene kadar boş görünürdü. setTimeout
  // arka planda da (kısılmış olsa bile) çalıştığı için güvenli sondur.
  failsafe = setTimeout(function () {
    if (typer === handle) finish();
  }, dur + 2000);
  return handle;
}

function stopTyping() {
  if (typer) typer.finish();
}

// ─────────────────────────────────────────── mesaj görüntüleme
function clearWelcome() {
  var w = $("welcome");
  if (w) w.remove();
}

function addMessage(role, text, animate) {
  clearWelcome();
  var wrap = document.createElement("div");
  wrap.className = "msg " + role;
  var isUser = role === "user";
  wrap.innerHTML =
    '<div class="msg-inner">' +
      '<div class="avatar">' + (isUser ? "👤" : "⚛") + "</div>" +
      '<div class="body">' +
        '<div class="role">' + (isUser ? t("you") : t("bot")) + "</div>" +
        '<div class="content"></div>' +
      "</div>" +
    "</div>";
  var content = wrap.querySelector(".content");
  var html = isUser ? "<p>" + inline(text) + "</p>" : markdown(text);
  chat.appendChild(wrap);

  if (animate) {
    typeInto(content, html, function () { bindCopy(content); });
  } else {
    content.innerHTML = html;
    bindCopy(content);
  }
  scrollDown();
  return content;
}

function bindCopy(root) {
  root.querySelectorAll(".copy-btn").forEach(function (b) {
    b.addEventListener("click", function () {
      var code = decodeURIComponent(b.dataset.code || "");
      var done = function () {
        b.textContent = t("copied"); b.classList.add("done");
        setTimeout(function () {
          b.textContent = t("copy"); b.classList.remove("done");
        }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(code).then(done, function () {});
      } else {
        var ta = document.createElement("textarea");
        ta.value = code; document.body.appendChild(ta); ta.select();
        try { document.execCommand("copy"); done(); } catch (e) {}
        ta.remove();
      }
    });
  });
}

function scrollDown() { chat.scrollTop = chat.scrollHeight; }

// ─────────────────────────────────────────── gönderme
function send(text) {
  text = (text || input.value).trim();
  if (!text || busy) return;
  stopTyping();               // önceki cevap hâlâ yazılıyorsa hemen tamamla
  busy = true;
  sendBtn.disabled = true;
  input.value = "";
  autoGrow();
  addMessage("user", text, false);
  $("thinkingBadge").classList.remove("hidden");

  api("/api/sohbet", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mesaj: text, oturum: SESSION, dil: LANG })
  })
  .then(function (r) { return r.json(); })
  .then(function (d) {
    // Sekme arka plandaysa efekti hiç başlatma: animasyon karesi gelmez.
    addMessage("bot", d.text || "…", TYPING && !document.hidden);
  })
  .catch(function () {
    addMessage("bot", "⚠️ " + t("err"), false);
  })
  .then(function () {
    busy = false;
    sendBtn.disabled = false;
    $("thinkingBadge").classList.add("hidden");
    input.focus();
    loadSessions();          // başlık ilk mesajdan gelir, listeyi tazele
  });
}

function autoGrow() {
  // Kutu boşken satır içi yüksekliği tamamen kaldırıyoruz; böylece CSS'teki
  // tek satırlık hâline döner. Ölçüme güvenip "auto" üzerinden hesaplamak,
  // bazı durumlarda bayat bir scrollHeight okuyup kutuyu 200px'e kilitliyordu.
  if (!input.value) { input.style.height = ""; return; }
  // Sekme arka plandayken (veya pencere gizliyken) genişlik 0 ölçülür; o anda
  // tek satır onlarca satıra sarılmış gibi görünüp kutuyu 200px'e kilitler.
  // Ölçemiyorsak dokunmuyoruz.
  if (!input.clientWidth) return;
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 200) + "px";
}

// ─────────────────────────────────────────── dosya yükleme
var MAX_DOSYA = 60 * 1024 * 1024;

function boyutMetni(n) {
  if (n < 1024) return n + " B";
  if (n < 1024 * 1024) return (n / 1024).toFixed(1) + " KB";
  return (n / 1024 / 1024).toFixed(1) + " MB";
}

function dosyaSimgesi(ad) {
  var u = (ad.split(".").pop() || "").toLowerCase();
  if (u === "pdf") return "📕";
  if (["png","jpg","jpeg","gif","webp","bmp","tif","tiff"].indexOf(u) >= 0) return "🖼️";
  if (["m","py","c","cpp","jl","r","ipynb"].indexOf(u) >= 0) return "💻";
  return "📄";
}

// Kullanıcı tarafında dosyayı bir "mesaj" olarak göster
function dosyaBaloncugu(file) {
  clearWelcome();
  var wrap = document.createElement("div");
  wrap.className = "msg user";
  wrap.innerHTML =
    '<div class="msg-inner"><div class="avatar">👤</div>' +
    '<div class="body"><div class="role">' + t("you") + "</div>" +
    '<div class="content"></div></div></div>';
  var c = wrap.querySelector(".content");
  var chip = document.createElement("div");
  chip.className = "file-chip";
  chip.innerHTML = '<span class="fc-icon">' + dosyaSimgesi(file.name) + "</span>" +
                   "<span></span><span class='fc-size'>" +
                   boyutMetni(file.size) + "</span>";
  chip.children[1].textContent = file.name;
  c.appendChild(chip);
  if (/^image\//.test(file.type)) {
    var img = document.createElement("img");
    img.className = "file-prev";
    img.src = URL.createObjectURL(file);
    img.onload = function () { scrollDown(); };
    c.appendChild(img);
  }
  chat.appendChild(wrap);
  scrollDown();
}

function dosyaYukle(files) {
  if (!files || !files.length || busy) return;
  var liste = [];
  for (var i = 0; i < files.length && i < 5; i++) {
    if (files[i].size > MAX_DOSYA) {
      addMessage("bot", "⚠️ **" + files[i].name + "** — " + t("tooBig"), false);
      continue;
    }
    liste.push(files[i]);
  }
  if (!liste.length) return;

  stopTyping();
  busy = true;
  sendBtn.disabled = true;
  $("attachBtn").disabled = true;
  liste.forEach(dosyaBaloncugu);
  $("thinkingBadge").classList.remove("hidden");

  var fd = new FormData();
  fd.append("oturum", SESSION);
  fd.append("dil", LANG);
  liste.forEach(function (f) { fd.append("dosya", f, f.name); });

  api("/api/yukle", { method: "POST", body: fd })
  .then(function (r) { return r.json(); })
  .then(function (d) {
    if (d.hata) { addMessage("bot", "⚠️ " + d.hata, false); return; }
    (d.sonuclar || []).forEach(function (s) {
      addMessage("bot", s.text || "…", TYPING && !document.hidden);
    });
  })
  .catch(function () { addMessage("bot", "⚠️ " + t("uploadErr"), false); })
  .then(function () {
    busy = false;
    sendBtn.disabled = false;
    $("attachBtn").disabled = false;
    $("thinkingBadge").classList.add("hidden");
    loadSessions();
    input.focus();
  });
}

// ─────────────────────────────────────────── öneriler
function loadSuggestions() {
  var box = $("suggestions");
  if (!box) return;
  api("/api/oneriler").then(function (r) { return r.json(); })
  .then(function (d) {
    var list = (d.oneriler && d.oneriler[LANG]) || [];
    box.innerHTML = "";
    list.forEach(function (s) {
      // button: fare kadar klavyeyle de kullanilabilsin
      var el = document.createElement("button");
      el.type = "button";
      el.className = "sugg";
      el.innerHTML = "<b>" + esc(s.baslik) + "</b><span>" + esc(s.metin) + "</span>";
      el.addEventListener("click", function () { send(s.metin); });
      box.appendChild(el);
    });
  }).catch(function () {});
}

// ─────────────────────────────────────────── durum yenileme
function fmt(n) {
  return (n || 0).toLocaleString(LANG === "tr" ? "tr-TR" : "en-US");
}

function refreshStatus() {
  api("/api/durum").then(function (r) { return r.json(); })
  .then(function (s) {
    $("sPapers").textContent   = fmt(s.makale);
    $("sConcepts").textContent = fmt(s.kavram);
    $("sLinks").textContent    = fmt(s.baglanti);
    $("sTerms").textContent    = fmt(s.terim);
    if ($("sInsights")) $("sInsights").textContent = fmt(s.bulgu);
    if ($("sDocs")) $("sDocs").textContent = fmt(s.belge);
    // Katli durum satiri: acmadan da ne durumda oldugu gorulsun
    var sl = $("statusLine");
    if (sl) {
      var durumMetni = s.calisiyor
        ? (LANG === "tr" ? "öğreniyor" : "learning")
        : (LANG === "tr" ? "duraklatıldı" : "paused");
      sl.textContent = fmt(s.makale) + (LANG === "tr" ? " makale · " : " papers · ")
                     + fmt(s.konu_sayisi + (s.ogrenilen_konu || 0))
                     + (LANG === "tr" ? " konu · " : " topics · ")
                     + durumMetni;
    }
    var sd = $("statusDot");
    if (sd) sd.className = "dot" + (s.calisiyor ? " on" : "");
    $("sTopics").textContent   = fmt(s.konu_sayisi);
    $("sFormulas").textContent = fmt(s.formul_sayisi);
    $("sConst").textContent    = fmt(s.sabit_sayisi);

    var lm = s.dil_modeli || {};
    var li = $("llmInfo"), ld = $("llmDot");
    if (li) {
      if (lm.model) {
        li.innerHTML = "<b>" + esc(lm.model.replace(".gguf", "").slice(0, 26)) +
                       "</b><br><span class='meta'>" + (lm.boyut_mb || 0) +
                       " MB · " + (lm.yuklu ? t("llmLoaded") : t("llmReady")) +
                       "</span>";
      } else {
        li.innerHTML = "<span class='meta'>" + t("llmNone") + "</span>";
      }
    }
    if (ld) ld.classList.toggle("live", !!lm.model);

    $("engineDot").classList.toggle("live", !!s.calisiyor);
    var te = $("toggleEngine");
    te.dataset.running = s.calisiyor ? "1" : "0";
    te.textContent = s.calisiyor ? t("stop") : t("start");

    var lb = $("logBox");
    if (!lb.classList.contains("hidden")) {
      lb.textContent = (s.log || []).join("\n");
      lb.scrollTop = lb.scrollHeight;
    }
  }).catch(function () {
    $("engineDot").classList.remove("live");
  });
}

// ─────────────────────────────────────────── sohbet listesi
function loadSessions() {
  api("/api/oturumlar").then(function (r) { return r.json(); })
  .then(function (d) {
    var box = $("sessionList");
    var list = d.oturumlar || [];
    // Sunucuya yazma kuyruk üzerinden gittiği için, az önce başlatılan sohbet
    // listede henüz görünmeyebilir. Ekranda mesaj varsa onu başa ekliyoruz ki
    // aktif sohbet her zaman vurgulanmış görünsün.
    if (!list.some(function (s) { return s.id === SESSION; })) {
      var firstUser = chat.querySelector(".msg.user .content");
      if (firstUser) {
        list.unshift({ id: SESSION, title: firstUser.textContent.trim(), n: 1 });
      }
    }
    box.innerHTML = "";
    if (!list.length) {
      box.innerHTML = '<div class="session-empty">' + t("noHistory") + "</div>";
      return;
    }
    list.forEach(function (s) {
      var el = document.createElement("div");
      el.className = "session-item" + (s.id === SESSION ? " active" : "");
      var title = (s.title || "").trim() || t("untitled");
      el.innerHTML = '<span class="s-title"></span>' +
                     '<button class="s-del" title="' + t("del") + '">×</button>';
      el.querySelector(".s-title").textContent = title;
      el.addEventListener("click", function (e) {
        if (e.target.closest(".s-del")) return;
        openSession(s.id);
      });
      el.querySelector(".s-del").addEventListener("click", function (e) {
        e.stopPropagation();
        deleteSession(s.id);
      });
      box.appendChild(el);
    });
  }).catch(function () {});
}

function openSession(id) {
  if (id === SESSION) return;
  stopTyping();
  SESSION = id;
  localStorage.setItem("pp_session", SESSION);
  chat.innerHTML = "";
  loadHistory(function () {
    if (!chat.children.length) showWelcome();
  });
  loadSessions();
  $("sidebar").classList.remove("open");
}

// Tum sohbet gecmisini sil. YALNIZCA konusma dokumu gider; sistemin
// bu sohbetlerden ogrendikleri (makale, kavram, formul, bulgu) kalir.
// Geri alinamayan bir islem oldugu icin once onay soruluyor.
function clearAllSessions() {
  if (!window.confirm(t("clearAllAsk"))) return;
  var btn = $("clearAll");
  if (btn) { btn.disabled = true; btn.textContent = "…"; }
  api("/api/tum-sohbetleri-sil", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({})
  }).then(function (r) { return r.json(); })
  .then(function (d) {
    SESSION = "s" + Date.now();
    localStorage.setItem("pp_session", SESSION);
    chat.innerHTML = "";
    showWelcome();
    loadSessions();
    var n = (d && d.silinen && d.silinen.sohbet) || 0;
    if (btn) {
      btn.disabled = false;
      btn.textContent = n + " " + t("clearAllDone");
      setTimeout(function () { btn.textContent = t("clearAll"); }, 2500);
    }
  }).catch(function () {
    if (btn) { btn.disabled = false; btn.textContent = t("clearAll"); }
  });
}

function deleteSession(id) {
  api("/api/oturum-sil", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ oturum: id })
  }).then(function () {
    if (id === SESSION) {
      SESSION = "s" + Date.now();
      localStorage.setItem("pp_session", SESSION);
      chat.innerHTML = "";
      showWelcome();
    }
    loadSessions();
  }).catch(function () {});
}

function showWelcome() {
  chat.innerHTML =
    '<div id="welcome">' +
      '<div class="hero-logo">⚛</div><h1>ParguszPhysics</h1>' +
      '<p class="hero-sub" data-i18n="heroSub"></p>' +
      '<div id="suggestions" class="suggestions"></div>' +
    "</div>";
  applyLang();
}

// ─────────────────────────────────────────── geçmiş
function loadHistory(done) {
  api("/api/gecmis?oturum=" + encodeURIComponent(SESSION))
  .then(function (r) { return r.json(); })
  .then(function (d) {
    var msgs = d.mesajlar || [];
    // Geçmiş anında gösterilir; yazma efekti yalnızca yeni cevaplarda
    msgs.forEach(function (m) {
      addMessage(m.role === "user" ? "user" : "bot", m.content, false);
    });
    if (done) done();
  }).catch(function () { if (done) done(); });
}

// ─────────────────────────────────────────── olaylar
sendBtn.addEventListener("click", function () { send(); });

input.addEventListener("keydown", function (e) {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
});
input.addEventListener("input", autoGrow);

// Yazma efektini atlamanın üç yolu: Esc, mesaja tıklama, efekt anahtarı
document.addEventListener("keydown", function (e) {
  if (e.key === "Escape") stopTyping();
});
// Kullanıcı başka sekmeye geçerse yazmayı hemen bitir; geri döndüğünde
// yarım kalmış bir mesajla karşılaşmasın.
document.addEventListener("visibilitychange", function () {
  if (document.hidden) stopTyping();
});
chat.addEventListener("click", function (e) {
  // kopyala düğmesine veya bağlantıya tıklamayı bozmayalım
  if (e.target.closest && e.target.closest(".copy-btn, a")) return;
  stopTyping();
});

$("typingToggle").addEventListener("click", function () {
  TYPING = !TYPING;
  localStorage.setItem("pp_typing", TYPING ? "1" : "0");
  if (!TYPING) stopTyping();
  applyLang();
});

// Yeni sohbet ESKİSİNİ SİLMEZ; yalnızca yeni bir oturum açar. Eski sohbet
// kenar çubuğundaki listede durur ve tıklayınca geri açılır.
$("newChat").addEventListener("click", function () {
  stopTyping();
// "Tümünü sil" düğmesi
(function () {
  var b = document.getElementById("clearAll");
  if (b) b.addEventListener("click", clearAllSessions);
})();
  SESSION = "s" + Date.now();
  localStorage.setItem("pp_session", SESSION);
  showWelcome();
  loadSessions();
});

$("toggleEngine").addEventListener("click", function () {
  var running = this.dataset.running === "1";
  api("/api/ogrenme", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ islem: running ? "dur" : "basla" })
  }).then(refreshStatus).catch(function () {});
});

$("showLog").addEventListener("click", function () {
  $("logBox").classList.toggle("hidden");
  refreshStatus();
});

document.querySelectorAll(".lang").forEach(function (b) {
  b.addEventListener("click", function () {
    LANG = b.dataset.lang;
    localStorage.setItem("pp_lang", LANG);
    applyLang();
  });
});

$("attachBtn").addEventListener("click", function () { $("fileInput").click(); });
$("fileInput").addEventListener("change", function () {
  dosyaYukle(this.files);
  this.value = "";           // aynı dosya tekrar seçilebilsin
});

// Sürükle-bırak
var suruklemeSayaci = 0;
["dragenter", "dragover"].forEach(function (ev) {
  document.addEventListener(ev, function (e) {
    if (!e.dataTransfer || (e.dataTransfer.types || []).indexOf("Files") < 0) return;
    e.preventDefault();
    if (ev === "dragenter") suruklemeSayaci++;
    $("dropHint").classList.remove("hidden");
  });
});
document.addEventListener("dragleave", function () {
  suruklemeSayaci = Math.max(0, suruklemeSayaci - 1);
  if (!suruklemeSayaci) $("dropHint").classList.add("hidden");
});
document.addEventListener("drop", function (e) {
  if (!e.dataTransfer || !e.dataTransfer.files.length) return;
  e.preventDefault();
  suruklemeSayaci = 0;
  $("dropHint").classList.add("hidden");
  dosyaYukle(e.dataTransfer.files);
});

// Panodan resim/dosya yapıştırma
input.addEventListener("paste", function (e) {
  var items = (e.clipboardData || {}).items || [];
  var dosyalar = [];
  for (var i = 0; i < items.length; i++) {
    if (items[i].kind === "file") {
      var f = items[i].getAsFile();
      if (f) dosyalar.push(f);
    }
  }
  if (dosyalar.length) { e.preventDefault(); dosyaYukle(dosyalar); }
});

$("menuBtn").addEventListener("click", function () {
  $("sidebar").classList.toggle("open");
});
chat.addEventListener("click", function () {
  $("sidebar").classList.remove("open");
});

// ─────────────────────────────────────────── başlangıç
// Sunucu güncellendiği hâlde eski arayüz açık kalırsa, kullanıcı düzeltilmiş
// davranışı göremez (ör. "yeni sohbet" eski sürümde geçmişi siliyordu).
// Sürümler tutmuyorsa önbelleği atlayarak bir kez yeniden yüklüyoruz.
// ─────────────────────────────────────────── bağlantı ayarı
// Arayüz GitHub Pages'ten açıldığında motorun adresi bilinmez; bir kez
// sorulur ve tarayıcıda saklanır. Bağlantı koparsa aynı ekran döner.
function baglantiEkrani(mesaj, onerilenAdres) {
  if (document.getElementById("pp-baglanti")) return;
  var d = document.createElement("div");
  d.id = "pp-baglanti";
  d.style.cssText = "position:fixed;inset:0;z-index:9999;display:flex;" +
    "align-items:center;justify-content:center;background:rgba(0,0,0,.72);" +
    "backdrop-filter:blur(4px);padding:20px";
  d.innerHTML =
    '<div style="max-width:460px;width:100%;background:var(--bg,#15161a);' +
    'color:var(--fg,#e8e8ea);border:1px solid rgba(255,255,255,.12);' +
    'border-radius:14px;padding:22px 24px;font:14px/1.55 system-ui,sans-serif">' +
    '<div style="font-size:17px;font-weight:600;margin-bottom:6px">' +
    'ParguszPhysics sunucusuna bağlan</div>' +
    '<div style="opacity:.75;margin-bottom:16px">' + (mesaj ||
      "Bu arayüz GitHub Pages'ten açıldı. Hesaplamaları yapan motor " +
      "başka bir bilgisayarda çalışıyor; adresini bir kez girin.") +
    '</div>' +
    '<label style="display:block;margin-bottom:4px;opacity:.8">Sunucu adresi</label>' +
    '<input id="pp-adres" placeholder="https://xxxx.trycloudflare.com" ' +
    'style="width:100%;padding:9px 11px;border-radius:9px;margin-bottom:12px;' +
    'border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.05);' +
    'color:inherit;font:inherit">' +
    '<label style="display:block;margin-bottom:4px;opacity:.8">Erişim anahtarı</label>' +
    '<input id="pp-anahtar" type="password" placeholder="sunucuda belirlediğiniz anahtar" ' +
    'style="width:100%;padding:9px 11px;border-radius:9px;margin-bottom:16px;' +
    'border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.05);' +
    'color:inherit;font:inherit">' +
    '<button id="pp-kaydet" style="width:100%;padding:10px;border:0;' +
    'border-radius:9px;background:#5b8cff;color:#fff;font:600 14px system-ui;' +
    'cursor:pointer">Bağlan</button>' +
    '<div id="pp-durum" style="margin-top:12px;opacity:.75;min-height:18px"></div>' +
    '</div>';
  document.body.appendChild(d);
  var adres = document.getElementById("pp-adres");
  var anahtar = document.getElementById("pp-anahtar");
  // Kutuda ESKI adresin durmasi kullaniciyi yaniltiyordu: sunucu
  // calisiyor olsa bile "Load failed" aliyordu. Yayimlanan adres
  // biliniyorsa onu yaziyoruz.
  adres.value = onerilenAdres || SUNUCU.adres;
  anahtar.value = SUNUCU.anahtar;
  var durum = document.getElementById("pp-durum");

  function dene() {
    durum.textContent = "Bağlanılıyor…";
    SUNUCU.kur(adres.value, anahtar.value);
    api("/api/surum")
      .then(function (r) {
        if (!r.ok) throw new Error(r.status === 403
          ? "Anahtar kabul edilmedi." : ("Sunucu " + r.status + " döndü."));
        return r.json();
      })
      .then(function () {
        d.remove();
        location.reload();
      })
      .catch(function (e) {
        durum.textContent = "Bağlanamadım: " + (e.message || e) +
          " — adres doğru mu, sunucu açık mı?";
      });
  }
  document.getElementById("pp-kaydet").onclick = dene;
  adres.onkeydown = anahtar.onkeydown = function (ev) {
    if (ev.key === "Enter") dene();
  };
}

// Ayarı sonradan değiştirebilmek için: konsoldan ya da adres çubuğuna
// #baglanti yazarak.
window.parguszBaglanti = baglantiEkrani;

// ── Otomatik bağlanma ──────────────────────────────────────────────────
// Ücretsiz tünel adresi her açılışta değişir; kullanıcıyı her seferinde
// adres girmeye zorlamak kabul edilemez. Çözüm iki parçalı:
//
//   ANAHTAR : bir kereye mahsus bağlantıdaki #anahtar=... ile gelir ve
//             tarayıcıda saklanır. Depoda DURMAZ — depo herkese açık.
//   ADRES   : sunucu her açılışta güncel adresi sunucu.json dosyasına
//             yazıp GitHub'a gönderir; sayfa onu kendisi okur.
//
// Böylece kullanıcı ilk seferden sonra hiçbir şey girmez.

// 1. Adres çubuğundaki anahtarı al ve gizle (geçmişte kalmasın)
(function () {
  var m = (location.hash || "").match(/anahtar=([^&]+)/);
  if (m) {
    SUNUCU.kur(SUNUCU.adres, decodeURIComponent(m[1]));
    try {
      history.replaceState(null, "", location.pathname + location.search);
    } catch (e) { location.hash = ""; }
  }
})();

// 2. Sunucunun yayımladığı güncel adresi oku
function yayinlananAdres() {
  return fetch("sunucu.json?t=" + Date.now(), { cache: "no-store" })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (j) { return (j && j.adres) ? j.adres : null; })
    .catch(function () { return null; });
}

// 3. Bir adresin gerçekten çalıştığını sına
function adresCalisiyorMu() {
  return api("/api/surum")
    .then(function (r) { return r.ok; })
    .catch(function () { return false; });
}

// Tünel her yeniden başladığında adres DEĞİŞİR. Yayımlanan adresin
// GitHub Pages önbelleğine düşmesi bir iki dakika sürebiliyor; o arada
// sayfa açılırsa eski adres okunuyor ve kullanıcı elle düzeltmek zorunda
// kalıyordu (ölçüldü: motor, tünel ve anahtar çalışırken bile bağlantı
// ekranında eski adres duruyordu). Bu yüzden birkaç kez, artan aralıkla
// yeniden bakıyoruz.
function adresAra(kalan, oncekiAdres) {
  return yayinlananAdres().then(function (adres) {
    if (adres && adres !== oncekiAdres) {
      SUNUCU.kur(adres, SUNUCU.anahtar);
      return adresCalisiyorMu().then(function (oldu) {
        if (oldu) return adres;
        return kalan > 0
          ? bekle(3000).then(function () { return adresAra(kalan - 1, adres); })
          : null;
      });
    }
    if (kalan > 0) {
      return bekle(3000).then(function () {
        return adresAra(kalan - 1, oncekiAdres);
      });
    }
    return null;
  });
}

function bekle(ms) {
  return new Promise(function (c) { setTimeout(c, ms); });
}

function otomatikBaglan() {
  // Önce elimizdeki adresi dene
  adresCalisiyorMu().then(function (tamam) {
    if (tamam) return;
    // Olmadıysa sunucunun yayımladığı adresi al ve onu dene
    yayinlananAdres().then(function (ilk) {
      if (!ilk) {
        return baglantiEkrani(
          "Sunucuya ulaşamadım. Motorun açık olduğundan emin olun.");
      }
      SUNUCU.kur(ilk, SUNUCU.anahtar);
      adresCalisiyorMu().then(function (oldu) {
        if (oldu) return location.reload();
        if (!SUNUCU.anahtar) {
          return baglantiEkrani(
            "Sunucuyu buldum ama erişim anahtarı gerekiyor. " +
            "Size verilen bağlantıyı kullanın ya da anahtarı buraya girin.");
        }
        // Adres eski olabilir: yayımlanan adres güncellenene kadar bekle
        baglantiEkrani("Sunucu adresini arıyorum…", ilk);
        adresAra(3, ilk).then(function (bulundu) {
          if (bulundu) return location.reload();
          var d = document.getElementById("pp-durum");
          if (d) {
            d.textContent = "Yayımlanan adres hâlâ yanıt vermiyor. " +
              "Motorun açık olduğundan emin olup Bağlan'a basın.";
          }
        });
      });
    });
  });
}

if (location.hash === "#baglanti") {
  baglantiEkrani("Bağlantı ayarları.");
} else {
  otomatikBaglan();
}

api("/api/surum").then(function (r) { return r.json(); })
.then(function (d) {
  if (d.surum && d.surum !== UI_SURUM && !sessionStorage.getItem("pp_reloaded")) {
    sessionStorage.setItem("pp_reloaded", "1");
    location.reload(true);
  }
}).catch(function () {});

applyLang();
loadHistory(function () { if (!chat.children.length) showWelcome(); });
loadSessions();
refreshStatus();
setInterval(refreshStatus, 4000);
input.focus();

})();
