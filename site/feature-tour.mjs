import { tourLabels, tourSections } from "./feature-tour-content.mjs";

const mount = document.querySelector("[data-feature-tour]");
const launch = document.querySelector("[data-feature-tour-launch]");
const sectionKey = mount?.dataset.featureTour;
const section = tourSections[sectionKey];

if (section && launch) {
  const pageUrl = new URL(window.location.href);
  const tourUrl = key => {
    const url = new URL(tourSections[key].path, import.meta.url);
    url.searchParams.set("tour", "1");
    return url;
  };
  const sectionName = (key, language) => {
    if (language === "fr" && key === "explorer") return "l’explorateur de données d’Info Source";
    return tourSections[key].name;
  };

  mount.innerHTML = `
    <section id="feature-tour" class="feature-tour" aria-labelledby="feature-tour-heading" hidden>
      <div class="feature-tour__header">
        <h2 id="feature-tour-heading" tabindex="-1"></h2>
        <button class="feature-tour__close" type="button"></button>
      </div>
      <nav class="feature-tour__sections" aria-labelledby="feature-tour-heading"></nav>
      <div class="feature-tour__card">
        <div class="feature-tour__content" aria-live="polite" aria-atomic="true">
          <p class="feature-tour__count"></p>
          <h3></h3>
          <p class="feature-tour__copy"></p>
          <p class="feature-tour__example" hidden></p>
        </div>
        <a class="feature-tour__action"></a>
      </div>
      <div class="feature-tour__footer">
        <div class="feature-tour__arrows">
          <button class="feature-tour__previous" type="button"><span aria-hidden="true">←</span></button>
          <button class="feature-tour__next" type="button"><span aria-hidden="true">→</span></button>
        </div>
        <a class="feature-tour__next-page"></a>
      </div>
    </section>`;

  const find = selector => mount.querySelector(selector);
  const panel = find("#feature-tour");
  const heading = find("#feature-tour-heading");
  const closeButton = find(".feature-tour__close");
  const navigation = find(".feature-tour__sections");
  const count = find(".feature-tour__count");
  const cardHeading = find(".feature-tour__card h3");
  const copy = find(".feature-tour__copy");
  const example = find(".feature-tour__example");
  const action = find(".feature-tour__action");
  const previous = find(".feature-tour__previous");
  const next = find(".feature-tour__next");
  const nextPage = find(".feature-tour__next-page");
  const sections = Object.keys(tourSections).map(key => {
    const link = document.createElement("a");
    link.href = tourUrl(key);
    if (key === sectionKey) link.setAttribute("aria-current", "page");
    navigation.append(link);
    return { key, link };
  });
  nextPage.href = tourUrl(section.next);
  launch.setAttribute("aria-controls", panel.id);
  launch.setAttribute("aria-expanded", "false");

  let index = 0;
  const language = () => section.fr && document.documentElement.lang.startsWith("fr") ? "fr" : "en";
  const cards = () => section[language()];

  function renderCard() {
    const steps = cards();
    const card = steps[index];
    count.textContent = tourLabels[language()].count(index + 1, steps.length);
    cardHeading.textContent = card.title;
    copy.textContent = card.copy;
    example.hidden = !card.example;
    example.textContent = card.example ?? "";
    action.textContent = card.action;
    action.href = card.href.startsWith("#") ? card.href : new URL(card.href, import.meta.url);
    previous.setAttribute("aria-disabled", String(index === 0));
    next.setAttribute("aria-disabled", String(index === steps.length - 1));
  }

  function renderLanguage() {
    const locale = language();
    const labels = tourLabels[locale];
    launch.textContent = labels.launch;
    heading.textContent = labels.tours;
    closeButton.textContent = labels.close;
    previous.setAttribute("aria-label", labels.previous);
    next.setAttribute("aria-label", labels.next);
    previous.title = labels.previous;
    next.title = labels.next;
    for (const { key, link } of sections) link.textContent = sectionName(key, locale);
    const nextName = sectionName(section.next, locale);
    nextPage.textContent = section.next === "explorer" ? labels.firstSection(nextName) : labels.nextSection(nextName);
    renderCard();
  }

  function openTour() {
    panel.hidden = false;
    launch.setAttribute("aria-expanded", "true");
    heading.focus();
  }

  function closeTour(restoreFocus = true) {
    panel.hidden = true;
    launch.setAttribute("aria-expanded", "false");
    if (pageUrl.searchParams.has("tour")) {
      pageUrl.searchParams.delete("tour");
      window.history.replaceState(window.history.state, "", pageUrl);
    }
    if (restoreFocus) launch.focus();
  }

  function moveCard(delta) {
    const destination = index + delta;
    if (destination < 0 || destination >= cards().length) return;
    index = destination;
    renderCard();
  }

  launch.addEventListener("click", () => panel.hidden ? openTour() : closeTour());
  closeButton.addEventListener("click", () => closeTour());
  previous.addEventListener("click", () => moveCard(-1));
  next.addEventListener("click", () => moveCard(1));
  panel.addEventListener("keydown", event => {
    if (event.key === "Escape") {
      event.preventDefault();
      closeTour();
    } else if ((event.target === previous || event.target === next) &&
               (event.key === "ArrowLeft" || event.key === "ArrowRight")) {
      event.preventDefault();
      moveCard(event.key === "ArrowLeft" ? -1 : 1);
    }
  });
  action.addEventListener("click", event => {
    const { href } = cards()[index];
    if (!href.startsWith("#") || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    const selectors = sectionKey === "my-info"
      ? [href, "#persona-examples", "#results-region", "#loading", "#survey-main"]
      : [href];
    const target = selectors.map(selector => document.querySelector(selector))
      .find(element => element && !element.closest("[hidden]"));
    if (!target) return;

    closeTour(false);
    const details = target.matches("details") ? target : target.querySelector("details");
    // Expand the example picker before moving focus to its summary.
    if (details && (target.id === "persona-examples" || target.id === "identity-diagram")) {
      details.open = true;
      details.querySelector("summary").focus();
    } else {
      if (target.tabIndex < 0 && !target.hasAttribute("tabindex")) target.setAttribute("tabindex", "-1");
      target.focus();
    }
  });

  renderLanguage();
  if (section.fr) {
    new MutationObserver(renderLanguage).observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["lang"],
    });
  }
  mount.hidden = false;
  launch.hidden = false;
  if (pageUrl.searchParams.get("tour") === "1") openTour();
}
