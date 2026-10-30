(() => {
  "use strict";

  const form = document.querySelector(".search-controls");
  const query = document.querySelector("#search-query");
  const category = document.querySelector("#search-category");
  const year = document.querySelector("#search-year");
  const topic = document.querySelector("#search-topic");
  const count = document.querySelector("#search-count");
  const empty = document.querySelector("#search-empty");
  const cards = [...document.querySelectorAll(".search-result")];

  if (!form || !query || !category || !year || !topic || !count || !empty || !cards.length) return;

  const normalise = (value) => String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("it")
    .replace(/\s+/g, " ")
    .trim();

  const fallbackRecords = new Map(cards.map((card) => [
    card.dataset.dossier,
    normalise(card.textContent),
  ]));
  let records = fallbackRecords;

  const setControl = (control, value) => {
    if (control.tagName === "SELECT") {
      if ([...control.options].some((option) => option.value === value)) control.value = value;
      return;
    }
    control.value = value;
  };

  const readUrl = () => {
    const params = new URLSearchParams(location.search);
    query.value = params.get("q") || "";
    setControl(category, params.get("categoria") || "");
    setControl(year, params.get("anno") || "");
    setControl(topic, params.get("argomento") || "");
  };

  const writeUrl = () => {
    const params = new URLSearchParams();
    if (query.value.trim()) params.set("q", query.value.trim());
    if (category.value) params.set("categoria", category.value);
    if (year.value) params.set("anno", year.value);
    if (topic.value) params.set("argomento", topic.value);
    const next = params.size ? `${location.pathname}?${params}` : location.pathname;
    history.replaceState(null, "", next);
  };

  const applyFilters = () => {
    const wantedQuery = normalise(query.value);
    const wantedCategory = category.value;
    const wantedYear = year.value;
    const wantedTopic = normalise(topic.value);
    let visible = 0;

    cards.forEach((card) => {
      const haystack = records.get(card.dataset.dossier) || normalise(card.textContent);
      const matches = (!wantedQuery || haystack.includes(wantedQuery))
        && (!wantedCategory || card.dataset.category === wantedCategory)
        && (!wantedYear || card.dataset.year === wantedYear)
        && (!wantedTopic || haystack.includes(wantedTopic));
      card.hidden = !matches;
      if (matches) visible += 1;
    });

    count.textContent = `${visible} ${visible === 1 ? "indagine" : "indagini"}`;
    empty.hidden = visible !== 0;
    writeUrl();
  };

  form.addEventListener("input", applyFilters);
  form.addEventListener("change", applyFilters);
  form.addEventListener("reset", () => {
    requestAnimationFrame(applyFilters);
  });

  readUrl();
  applyFilters();

  fetch("search-index.json", { credentials: "same-origin" })
    .then((response) => {
      if (!response.ok) throw new Error("Indice non disponibile");
      return response.json();
    })
    .then((items) => {
      records = new Map(items.map((item) => [item.slug, normalise([
        item.title,
        item.description,
        item.category,
        ...(item.topics || []),
        item.text,
      ].join(" "))]));
      applyFilters();
    })
    .catch(() => {
      records = fallbackRecords;
    });
})();
