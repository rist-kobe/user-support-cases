(function () {
  "use strict";

  var DATA_URL = "data/cases.json";

  var state = {
    cases: [],
    caseTypeNames: {},
    category: "all",
    keyword: "",
    supportTags: new Set(),
    technicalTags: new Set(),
    allSupportTags: [],
    allTechnicalTags: [],
    lastFocusedElement: null,
  };

  var elements = {};

  function uid(caseItem) {
    return caseItem.case_type + "-" + caseItem.case_id;
  }

  function escapeHtml(str) {
    return String(str == null ? "" : str).replace(/[&<>"']/g, function (ch) {
      return (
        {
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;",
        }[ch] || ch
      );
    });
  }

  function matchesKeyword(caseItem, keyword) {
    if (!keyword) {
      return true;
    }
    var haystack = [
      caseItem.classification,
      caseItem.problem,
      caseItem.support_content,
      caseItem.support_result,
      caseItem.document,
    ]
      .filter(Boolean)
      .join("\n")
      .toLowerCase();
    return haystack.indexOf(keyword.toLowerCase()) !== -1;
  }

  function matchesTags(caseItem, selected, field) {
    if (selected.size === 0) {
      return true;
    }
    var tags = caseItem[field] || [];
    for (var tag of selected) {
      if (tags.indexOf(tag) === -1) {
        return false;
      }
    }
    return true;
  }

  function getFilteredCases() {
    return state.cases.filter(function (caseItem) {
      if (state.category !== "all" && caseItem.case_type !== state.category) {
        return false;
      }
      if (!matchesKeyword(caseItem, state.keyword)) {
        return false;
      }
      if (!matchesTags(caseItem, state.supportTags, "support_tags")) {
        return false;
      }
      if (!matchesTags(caseItem, state.technicalTags, "technical_tags")) {
        return false;
      }
      return true;
    });
  }

  function renderTagList(container, tags, selectedSet) {
    container.innerHTML = "";
    tags.forEach(function (tag) {
      var chip = document.createElement("button");
      chip.type = "button";
      chip.className = "tag-chip" + (selectedSet.has(tag) ? " selected" : "");
      chip.textContent = tag;
      chip.addEventListener("click", function () {
        if (selectedSet.has(tag)) {
          selectedSet.delete(tag);
        } else {
          selectedSet.add(tag);
        }
        renderAll();
      });
      container.appendChild(chip);
    });
  }

  function renderCaseCard(caseItem) {
    var card = document.createElement("button");
    card.type = "button";
    card.className = "case-card";
    card.setAttribute("data-uid", uid(caseItem));

    var tagsHtml = (caseItem.support_tags || [])
      .concat(caseItem.technical_tags || [])
      .map(function (tag) {
        return "<span>" + escapeHtml(tag) + "</span>";
      })
      .join("");

    card.innerHTML =
      '<div class="case-id">' +
      escapeHtml(state.caseTypeNames[caseItem.case_type] || caseItem.case_type_name || caseItem.case_type) +
      " / No." +
      escapeHtml(caseItem.case_id) +
      "</div>" +
      '<div class="case-classification">' +
      escapeHtml(caseItem.classification || "(分類未設定)") +
      "</div>" +
      '<div class="case-tags">' +
      tagsHtml +
      "</div>";

    card.addEventListener("click", function () {
      openDetail(caseItem);
    });

    return card;
  }

  function renderList() {
    var filtered = getFilteredCases();
    elements.caseList.innerHTML = "";

    if (filtered.length === 0) {
      var empty = document.createElement("div");
      empty.className = "empty-state";
      empty.textContent = "該当する事例が見つかりませんでした。";
      elements.caseList.appendChild(empty);
    } else {
      filtered.forEach(function (caseItem) {
        elements.caseList.appendChild(renderCaseCard(caseItem));
      });
    }

    elements.resultSummary.textContent =
      filtered.length + " / " + state.cases.length + " 件を表示中";
  }

  function renderAll() {
    renderTagList(elements.supportTagList, state.allSupportTags, state.supportTags);
    renderTagList(elements.technicalTagList, state.allTechnicalTags, state.technicalTags);
    renderList();
  }

  function numericField(label, value) {
    if (value === null || value === undefined) {
      return "";
    }
    return (
      "<section><h3>" +
      escapeHtml(label) +
      "</h3><p>" +
      escapeHtml(value) +
      "</p></section>"
    );
  }

  function textSection(label, value) {
    return (
      "<section><h3>" +
      escapeHtml(label) +
      '</h3><p class="field-text">' +
      escapeHtml(value || "") +
      "</p></section>"
    );
  }

  function tagSection(label, tags) {
    var content = (tags || [])
      .map(function (tag) {
        return "<span>" + escapeHtml(tag) + "</span>";
      })
      .join("");
    return (
      "<section><h3>" + escapeHtml(label) + '</h3><p class="case-tags">' + content + "</p></section>"
    );
  }

  function renderDetail(caseItem) {
    var html =
      '<div class="case-detail">' +
      "<h2>事例 No." +
      escapeHtml(caseItem.case_id) +
      "</h2>" +
      "<dl>" +
      "<dt>種別</dt><dd>" +
      escapeHtml(caseItem.case_type_name || caseItem.case_type) +
      "</dd>" +
      "<dt>分類</dt><dd>" +
      escapeHtml(caseItem.classification || "") +
      "</dd>" +
      "</dl>" +
      textSection("課題", caseItem.problem) +
      tagSection("支援タグ", caseItem.support_tags) +
      tagSection("技術タグ", caseItem.technical_tags) +
      textSection("支援内容", caseItem.support_content) +
      textSection("支援結果", caseItem.support_result) +
      textSection("本文（document）", caseItem.document) +
      numericField("高速化倍率 (speedup)", caseItem.speedup) +
      numericField(
        "性能改善率 (%)",
        caseItem.performance_improvement_percent
      ) +
      numericField("最大ノード数", caseItem.max_nodes) +
      numericField("最大スレッド数", caseItem.max_threads) +
      "</div>";

    elements.modalBody.innerHTML = html;
  }

  function showModal() {
    var activeElement = document.activeElement;
    if (activeElement && activeElement !== document.body && activeElement !== document.documentElement) {
      state.lastFocusedElement = activeElement;
    } else {
      state.lastFocusedElement = null;
    }

    elements.modalOverlay.hidden = false;
    if (elements.modalClose) {
      elements.modalClose.focus();
    }
  }

  function openDetail(caseItem) {
    renderDetail(caseItem);
    showModal();
    var params = new URLSearchParams(window.location.search);
    params.set("case", uid(caseItem));
    history.replaceState(null, "", "?" + params.toString());
  }

  function closeDetail() {
    elements.modalOverlay.hidden = true;
    if (
      state.lastFocusedElement &&
      typeof state.lastFocusedElement.focus === "function" &&
      document.contains(state.lastFocusedElement)
    ) {
      state.lastFocusedElement.focus();
    }
    state.lastFocusedElement = null;
    var params = new URLSearchParams(window.location.search);
    params.delete("case");
    var query = params.toString();
    history.replaceState(null, "", query ? "?" + query : window.location.pathname);
  }

  function openDetailFromQuery() {
    var params = new URLSearchParams(window.location.search);
    var caseUid = params.get("case");
    if (!caseUid) {
      return;
    }
    var found = state.cases.find(function (c) {
      return uid(c) === caseUid;
    });
    if (found) {
      renderDetail(found);
      showModal();
    }
  }

  function setupCategoryTabs() {
    var tabs = elements.categoryTabs.querySelectorAll(".tab");
    tabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        tabs.forEach(function (t) {
          t.classList.remove("active");
        });
        tab.classList.add("active");
        state.category = tab.getAttribute("data-category");
        renderAll();
      });
    });
  }

  function setupSearch() {
    elements.keywordInput.addEventListener("input", function (event) {
      state.keyword = event.target.value.trim();
      renderAll();
    });
  }

  function setupModal() {
    elements.modalClose.addEventListener("click", closeDetail);
    elements.modalOverlay.addEventListener("click", function (event) {
      var modalRect = elements.modalOverlay.querySelector(".modal").getBoundingClientRect();
      var isInsideModal =
        event.clientX >= modalRect.left &&
        event.clientX <= modalRect.right &&
        event.clientY >= modalRect.top &&
        event.clientY <= modalRect.bottom;
      if (!isInsideModal) {
        closeDetail();
      }
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !elements.modalOverlay.hidden) {
        closeDetail();
      }
    });
  }

  function init(payload) {
    state.cases = payload.cases || [];
    state.caseTypeNames = payload.case_types || {};

    elements.categoryTabs = document.getElementById("category-tabs");
    elements.keywordInput = document.getElementById("keyword-input");
    elements.caseList = document.getElementById("case-list");
    elements.resultSummary = document.getElementById("result-summary");
    elements.modalOverlay = document.getElementById("modal-overlay");
    elements.modalBody = document.getElementById("modal-body");
    elements.modalClose = document.getElementById("modal-close");
    elements.supportTagList = document.getElementById("support-tag-list");
    elements.technicalTagList = document.getElementById("technical-tag-list");

    state.allSupportTags = (payload.tags && payload.tags.support_tags) || [];
    state.allTechnicalTags = (payload.tags && payload.tags.technical_tags) || [];

    setupCategoryTabs();
    setupSearch();
    setupModal();

    renderAll();
    openDetailFromQuery();
  }

  function main() {
    fetch(DATA_URL)
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Failed to load " + DATA_URL);
        }
        return response.json();
      })
      .then(init)
      .catch(function (error) {
        var container = document.getElementById("case-list");
        if (container) {
          container.innerHTML =
            '<div class="empty-state">データの読み込みに失敗しました: ' +
            escapeHtml(error.message) +
            "</div>";
        }
        console.error(error);
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", main);
  } else {
    main();
  }
})();
