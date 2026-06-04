/* MetaMAVS team-introduction deck. Generated with pptxgenjs. */
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa6");

// ---------- palette ----------
const INK = "0C2233";    // deep ocean navy (dark bg)
const INK2 = "13344A";   // panel navy
const TEAL = "0E8388";   // primary brand
const TEALD = "0B6E72";
const MINT = "2DD4BF";   // accent
const AMBER = "F4A52A";  // sharp accent
const CORAL = "E5614C";  // critical
const CLOUD = "F4F7F9";  // light bg
const WHITE = "FFFFFF";
const SLATE = "556675";  // muted body
const DARK = "16323F";   // body on light
const LINE = "E2E8F0";

const H = "Trebuchet MS";
const B = "Calibri";

const W = 13.3, HT = 7.5, M = 0.62;

// ---------- icon rasteriser ----------
function svgOf(Icon, color, size = 256) {
  return ReactDOMServer.renderToStaticMarkup(React.createElement(Icon, { color, size: String(size) }));
}
async function icon(Icon, color) {
  const png = await sharp(Buffer.from(svgOf(Icon, color, 256))).png().toBuffer();
  return "image/png;base64," + png.toString("base64");
}
const shadow = () => ({ type: "outer", color: "0C2233", blur: 7, offset: 3, angle: 90, opacity: 0.16 });

let I = {}; // pre-rendered icons

async function prerender() {
  const map = {
    virus: [fa.FaVirus, WHITE], dna: [fa.FaDna, TEAL],
    flask: [fa.FaFlask, WHITE], robot: [fa.FaRobot, WHITE], seed: [fa.FaSeedling, WHITE],
    droplet: [fa.FaDroplet, WHITE], shield: [fa.FaShieldHalved, WHITE], diagram: [fa.FaDiagramProject, WHITE],
    user: [fa.FaUserCheck, WHITE], warn: [fa.FaTriangleExclamation, WHITE], check: [fa.FaCircleCheck, WHITE],
    layer: [fa.FaLayerGroup, WHITE], list: [fa.FaListCheck, WHITE], terminal: [fa.FaTerminal, WHITE],
    chart: [fa.FaChartLine, WHITE], glass: [fa.FaMagnifyingGlass, WHITE], file: [fa.FaFileLines, WHITE],
    gears: [fa.FaGears, WHITE], brain: [fa.FaBrain, WHITE], cubes: [fa.FaCubes, WHITE],
    filter: [fa.FaFilter, WHITE], clip: [fa.FaClipboardCheck, WHITE], branch: [fa.FaCodeBranch, WHITE],
    server: [fa.FaServer, WHITE],
    // teal-colored variants for light-slide circles handled inline
  };
  for (const k of Object.keys(map)) I[k] = await icon(map[k][0], map[k][1]);
  // extra colored variants
  I.checkTeal = await icon(fa.FaCircleCheck, TEAL);
  I.warnAmber = await icon(fa.FaTriangleExclamation, AMBER);
}

// ---------- shared slide furniture ----------
function iconCircle(slide, x, y, d, fill, iconData, iconScale = 0.55) {
  slide.addShape("oval", { x, y, w: d, h: d, fill: { color: fill }, shadow: shadow() });
  const p = (d * (1 - iconScale)) / 2;
  slide.addImage({ data: iconData, x: x + p, y: y + p, w: d * iconScale, h: d * iconScale });
}

function lightHeader(slide, kicker, title, pageNo) {
  slide.background = { color: CLOUD };
  // top-left motif squares
  slide.addShape("rect", { x: M, y: 0.5, w: 0.16, h: 0.16, fill: { color: TEAL } });
  slide.addShape("rect", { x: M + 0.2, y: 0.5, w: 0.16, h: 0.16, fill: { color: MINT } });
  slide.addText(kicker.toUpperCase(), { x: M, y: 0.72, w: 11, h: 0.3, fontFace: H, fontSize: 12, bold: true, color: TEAL, charSpacing: 3, margin: 0 });
  slide.addText(title, { x: M, y: 0.98, w: W - 2 * M, h: 0.7, fontFace: H, fontSize: 30, bold: true, color: INK, margin: 0 });
  // footer
  slide.addText("MetaMAVS — Metagenomic Multi-Agent Virus Surveillance", { x: M, y: HT - 0.42, w: 9, h: 0.3, fontFace: B, fontSize: 9, color: SLATE, margin: 0 });
  slide.addText(String(pageNo), { x: W - M - 0.6, y: HT - 0.42, w: 0.6, h: 0.3, fontFace: B, fontSize: 9, color: SLATE, align: "right", margin: 0 });
}

function darkBase(slide) {
  slide.background = { color: INK };
  // subtle corner accents
  slide.addShape("rect", { x: 0, y: 0, w: W, h: 0.12, fill: { color: TEAL } });
  slide.addShape("rect", { x: 0, y: 0, w: 4.4, h: 0.12, fill: { color: MINT } });
}

function card(slide, x, y, w, h, accent, fill = WHITE) {
  slide.addShape("rect", { x, y, w, h, fill: { color: fill }, line: { color: LINE, width: 1 }, shadow: shadow() });
  slide.addShape("rect", { x, y, w: 0.09, h, fill: { color: accent } });
}

// =================================================================
async function build() {
  await prerender();
  const pres = new pptxgen();
  pres.defineLayout({ name: "WIDE", width: W, height: HT });
  pres.layout = "WIDE";
  pres.author = "Sihua Peng";
  pres.title = "MetaMAVS — Team Introduction";

  // ---------- 1. TITLE ----------
  {
    const s = pres.addSlide();
    s.background = { color: INK };
    // big translucent panel right
    s.addShape("rect", { x: 8.7, y: 0, w: 4.6, h: HT, fill: { color: INK2 } });
    s.addShape("rect", { x: 8.7, y: 0, w: 0.09, h: HT, fill: { color: MINT } });
    // virus icon cluster (non-overlapping)
    iconCircle(s, 9.55, 1.55, 1.45, TEAL, I.virus, 0.5);
    iconCircle(s, 11.3, 2.2, 0.9, MINT, I.diagram, 0.5);
    iconCircle(s, 9.45, 3.4, 0.95, AMBER, I.robot, 0.5);
    iconCircle(s, 10.85, 3.7, 1.1, TEALD, I.shield, 0.5);

    // left text
    s.addShape("rect", { x: M, y: 1.7, w: 0.5, h: 0.16, fill: { color: MINT } });
    s.addText("UGA · VIRAL EPIDEMIOLOGY · BIOINFORMATICS", { x: M, y: 1.95, w: 7.6, h: 0.3, fontFace: H, fontSize: 12, bold: true, color: MINT, charSpacing: 2, margin: 0 });
    s.addText("MetaMAVS", { x: M, y: 2.3, w: 8, h: 1.1, fontFace: H, fontSize: 62, bold: true, color: WHITE, margin: 0 });
    s.addText("Metagenomic Multi-Agent Virus Surveillance System", { x: M, y: 3.5, w: 7.7, h: 0.7, fontFace: H, fontSize: 21, color: "BFE9E6", margin: 0 });
    s.addText([
      { text: "A LangGraph-based, stateful multi-agent workflow for viral surveillance", options: { breakLine: true } },
      { text: "from wastewater, environmental & clinical metagenomic data.", options: {} },
    ], { x: M, y: 4.45, w: 7.6, h: 0.8, fontFace: B, fontSize: 14, color: "9FB3C0", lineSpacingMultiple: 1.15, margin: 0 });
    s.addText("Team Introduction  ·  Sihua Peng", { x: M, y: 5.9, w: 7, h: 0.4, fontFace: H, fontSize: 14, bold: true, color: WHITE, margin: 0 });
  }

  // ---------- 2. THE CHALLENGE ----------
  {
    const s = pres.addSlide();
    lightHeader(s, "Motivation", "Why MetaMAVS — the surveillance challenge", 2);
    const items = [
      ["droplet", "Complex, noisy data", "Wastewater & environmental metagenomes mix host, bacteria, phage and rare viral signals."],
      ["filter", "Many manual steps", "QC → host removal → detection → taxonomy → abundance → novelty: easy to break, hard to reproduce."],
      ["warn", "Risk of over-claiming", "Weak metagenomic hits can be mistaken for confirmed pathogens without careful flagging."],
      ["brain", "No coordination layer", "Traditional pipelines lack decision logic, human review, and error handling across steps."],
    ];
    const cw = (W - 2 * M - 0.5) / 2, ch = 2.05, gx = 0.5, gy = 0.45;
    items.forEach((it, i) => {
      const col = i % 2, row = Math.floor(i / 2);
      const x = M + col * (cw + gx), y = 1.95 + row * (ch + gy);
      card(s, x, y, cw, ch, TEAL);
      iconCircle(s, x + 0.32, y + 0.34, 0.78, TEAL, I[it[0]], 0.5);
      s.addText(it[1], { x: x + 1.3, y: y + 0.34, w: cw - 1.6, h: 0.5, fontFace: H, fontSize: 17, bold: true, color: INK, margin: 0 });
      s.addText(it[2], { x: x + 1.3, y: y + 0.86, w: cw - 1.6, h: 1.0, fontFace: B, fontSize: 13, color: SLATE, lineSpacingMultiple: 1.1, margin: 0 });
    });
    s.addText("MetaMAVS combines a deterministic bioinformatics pipeline with AI multi-agent coordination.", { x: M, y: 6.65, w: W - 2 * M, h: 0.4, fontFace: H, fontSize: 13, italic: true, bold: true, color: TEALD, align: "center", margin: 0 });
  }

  // ---------- 3. WHAT IS METAMAVS ----------
  {
    const s = pres.addSlide();
    lightHeader(s, "Overview", "What is MetaMAVS?", 3);
    s.addText("A research-grade system that processes metagenomic data, detects known & potential viral signals, classifies them, tracks abundance trends, assesses epidemiological risk, and writes surveillance reports — orchestrated as a LangGraph state machine.",
      { x: M, y: 1.9, w: W - 2 * M, h: 0.9, fontFace: B, fontSize: 15, color: DARK, lineSpacingMultiple: 1.15, margin: 0 });
    const cards = [
      ["flask", "Research-grade", "Scientifically cautious — \"detected signal\", not \"confirmed infection\". Never overstates weak evidence.", TEAL],
      ["robot", "Multi-agent", "Not a sequential script — a LangGraph StateGraph with 12 agent nodes & conditional routing.", AMBER],
      ["seed", "Evolvable", "Phase 1 is fully deterministic; clean seams let LLM reasoning slot into nodes later.", MINT],
    ];
    const cw = (W - 2 * M - 2 * 0.5) / 3, ch = 3.0, y = 3.05;
    cards.forEach((c, i) => {
      const x = M + i * (cw + 0.5);
      card(s, x, y, cw, ch, c[3]);
      iconCircle(s, x + 0.4, y + 0.4, 0.95, c[3], I[c[0]], 0.5);
      s.addText(c[1], { x: x + 0.4, y: y + 1.5, w: cw - 0.8, h: 0.5, fontFace: H, fontSize: 20, bold: true, color: INK, margin: 0 });
      s.addText(c[2], { x: x + 0.4, y: y + 2.05, w: cw - 0.8, h: 0.85, fontFace: B, fontSize: 13, color: SLATE, lineSpacingMultiple: 1.12, margin: 0 });
    });
  }

  // ---------- 4. DESIGN PHILOSOPHY ----------
  {
    const s = pres.addSlide();
    lightHeader(s, "Principles", "Core design philosophy", 4);
    const rows = [
      ["diagram", "State machine, not a script", "Conditional routing, error diversion, human-in-the-loop, checkpointing — impossible in a flat script."],
      ["cubes", "One shared state flows through", "Every node returns a partial update; warnings/errors/log use add-reducers to append, never overwrite."],
      ["layer", "Framework dependency centralized", "Only graph.py imports LangGraph; the 12 agents stay pure, testable functions."],
      ["branch", "Separation of concerns by layer", "Orchestration (LangGraph) · nodes (agents) · utilities · data validation (pydantic) — clearly split."],
      ["shield", "Scientific caution is enforced", "Phages flagged separately, low-confidence marked, confirmatory testing recommended for high risk."],
    ];
    let y = 1.95; const rh = 0.94, rg = 0.12;
    rows.forEach((r) => {
      card(s, M, y, W - 2 * M, rh, TEAL);
      iconCircle(s, M + 0.26, y + 0.17, 0.6, TEAL, I[r[0]], 0.5);
      s.addText(r[1], { x: M + 1.1, y: y + 0.12, w: 4.6, h: rh - 0.24, fontFace: H, fontSize: 15.5, bold: true, color: INK, valign: "middle", margin: 0 });
      s.addText(r[2], { x: M + 5.9, y: y + 0.12, w: W - 2 * M - 6.1, h: rh - 0.24, fontFace: B, fontSize: 12.5, color: SLATE, valign: "middle", lineSpacingMultiple: 1.05, margin: 0 });
      y += rh + rg;
    });
  }

  // ---------- 5. WORKFLOW AT A GLANCE ----------
  {
    const s = pres.addSlide();
    lightHeader(s, "Architecture", "The workflow at a glance — 12 nodes", 5);
    const nodes = [
      ["1", "input_manager", TEAL], ["2", "qc_agent", TEAL], ["3", "host_removal", TEAL], ["4", "viral_detection", TEAL],
      ["5", "taxonomy", TEAL], ["6", "abundance", TEAL], ["7", "novel_virus", TEAL], ["8", "risk_assessment", AMBER],
      ["9", "human_review", MINT], ["10", "report_writer", INK2], ["11", "final_summary", INK2], ["12", "error_handler", CORAL],
    ];
    const cols = 4, cw = 2.78, ch = 0.92, gx = 0.24, gy = 0.34;
    const x0 = M, y0 = 2.05;
    nodes.forEach((n, i) => {
      const col = i % cols, row = Math.floor(i / cols);
      const x = x0 + col * (cw + gx), y = y0 + row * (ch + gy);
      s.addShape("roundRect", { x, y, w: cw, h: ch, rectRadius: 0.08, fill: { color: WHITE }, line: { color: n[2], width: 1.5 }, shadow: shadow() });
      s.addShape("oval", { x: x + 0.16, y: y + 0.21, w: 0.5, h: 0.5, fill: { color: n[2] } });
      s.addText(n[0], { x: x + 0.16, y: y + 0.21, w: 0.5, h: 0.5, fontFace: H, fontSize: 15, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
      s.addText(n[1], { x: x + 0.78, y: y, w: cw - 0.9, h: ch, fontFace: H, fontSize: 13.5, bold: true, color: INK, valign: "middle", margin: 0 });
    });
    // arrows between rows (down-right snake hint) — simple chevrons at row ends
    const legendY = 5.95;
    const leg = [["Backbone analysis", TEAL], ["Decision point", AMBER], ["Human-in-the-loop", MINT], ["Report & summary", INK2], ["Error guard", CORAL]];
    let lx = M;
    leg.forEach((l) => {
      s.addShape("oval", { x: lx, y: legendY + 0.03, w: 0.2, h: 0.2, fill: { color: l[1] } });
      s.addText(l[0], { x: lx + 0.28, y: legendY - 0.04, w: 2.05, h: 0.3, fontFace: B, fontSize: 11, color: DARK, margin: 0 });
      lx += 2.35;
    });
    s.addText("START → input_manager → … → risk_assessment → (review?) → report_writer → final_summary → END.  Any node can divert to error_handler.",
      { x: M, y: 6.45, w: W - 2 * M, h: 0.5, fontFace: B, fontSize: 12, italic: true, color: SLATE, margin: 0 });
  }

  // ---------- 6. THE 12 AGENTS ----------
  {
    const s = pres.addSlide();
    lightHeader(s, "Agents", "What each node does", 6);
    const data = [
      ["glass", "viral_detection", "Generate Kraken2/DIAMOND etc. commands; produce raw hits + candidate taxa."],
      ["clip", "input_manager", "Validate manifest & metadata; emit a clean validated_manifest.csv."],
      ["check", "qc_agent", "FastQC/fastp/MultiQC commands; per-sample pass/fail."],
      ["filter", "host_removal", "Bowtie2/BWA/minimap2 commands; track non-host reads."],
      ["dna", "taxonomy", "Normalize taxa; flag phage / false-positive / low-complexity."],
      ["chart", "abundance", "RPM & genome-length normalization; cross-sample time trends."],
      ["virus", "novel_virus", "Assembly + VirSorter2/CheckV; surface novel/divergent candidates."],
      ["shield", "risk_assessment", "Fuse evidence → Low/Medium/High/Critical; set review flag."],
      ["user", "human_review", "HITL checkpoint on high risk (auto-approve in dry-run)."],
      ["file", "report_writer", "Assemble Markdown + HTML surveillance report."],
      ["list", "final_summary", "Final summary, report paths, persist state.json."],
      ["warn", "error_handler", "Classify errors, decide continue/stop, prevent silent failure."],
    ];
    // order to present in reading order matching node order
    const order = [1,2,3,0,4,5,6,7,8,9,10,11].map(i => data[i]);
    const cols = 3, cw = (W - 2 * M - 2 * 0.3) / 3, ch = 1.12, gx = 0.3, gy = 0.12, y0 = 1.85;
    order.forEach((d, i) => {
      const col = i % cols, row = Math.floor(i / cols);
      const x = M + col * (cw + gx), y = y0 + row * (ch + gy);
      card(s, x, y, cw, ch, TEAL);
      iconCircle(s, x + 0.22, y + 0.2, 0.54, TEAL, I[d[0]], 0.5);
      s.addText(d[1], { x: x + 0.9, y: y + 0.14, w: cw - 1.05, h: 0.4, fontFace: H, fontSize: 13, bold: true, color: INK, margin: 0 });
      s.addText(d[2], { x: x + 0.24, y: y + 0.58, w: cw - 0.45, h: 0.46, fontFace: B, fontSize: 10.5, color: SLATE, lineSpacingMultiple: 1.0, margin: 0 });
    });
  }

  // ---------- 7. ROUTING & HITL ----------
  {
    const s = pres.addSlide();
    lightHeader(s, "Control flow", "Smart routing, human review & error handling", 7);
    // risk box
    s.addShape("roundRect", { x: M, y: 2.7, w: 2.5, h: 1.0, rectRadius: 0.08, fill: { color: AMBER }, shadow: shadow() });
    s.addText("risk_assessment", { x: M, y: 2.7, w: 2.5, h: 1.0, fontFace: H, fontSize: 13.5, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
    // arrow risk -> router
    s.addShape("rightArrow", { x: M + 2.6, y: 3.05, w: 0.6, h: 0.3, fill: { color: SLATE } });
    // router
    s.addShape("roundRect", { x: 4.1, y: 2.55, w: 2.4, h: 1.3, rectRadius: 0.1, fill: { color: INK2 }, shadow: shadow() });
    s.addText("review_router\nreview required?", { x: 4.1, y: 2.55, w: 2.4, h: 1.3, fontFace: H, fontSize: 12.5, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
    // YES -> human_review (upper right)
    s.addShape("rightArrow", { x: 6.6, y: 2.32, w: 0.85, h: 0.26, fill: { color: MINT } });
    s.addText("YES", { x: 6.55, y: 2.0, w: 0.9, h: 0.3, fontFace: H, fontSize: 10, bold: true, color: TEALD, align: "center", margin: 0 });
    s.addShape("roundRect", { x: 7.55, y: 1.95, w: 2.5, h: 0.95, rectRadius: 0.08, fill: { color: MINT }, shadow: shadow() });
    s.addText("human_review", { x: 7.55, y: 1.95, w: 2.5, h: 0.95, fontFace: H, fontSize: 13.5, bold: true, color: INK, align: "center", valign: "middle", margin: 0 });
    // NO -> report (lower right)
    s.addShape("rightArrow", { x: 6.6, y: 3.55, w: 0.85, h: 0.26, fill: { color: TEAL } });
    s.addText("NO", { x: 6.55, y: 3.78, w: 0.9, h: 0.3, fontFace: H, fontSize: 10, bold: true, color: TEAL, align: "center", margin: 0 });
    s.addShape("roundRect", { x: 7.55, y: 3.4, w: 2.5, h: 0.95, rectRadius: 0.08, fill: { color: TEAL }, shadow: shadow() });
    s.addText("report_writer", { x: 7.55, y: 3.4, w: 2.5, h: 0.95, fontFace: H, fontSize: 13.5, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
    // human_review -> report (down arrow)
    s.addShape("downArrow", { x: 8.65, y: 2.9, w: 0.3, h: 0.5, fill: { color: SLATE } });
    // report -> final
    s.addShape("rightArrow", { x: 10.1, y: 3.75, w: 0.35, h: 0.26, fill: { color: SLATE } });
    s.addShape("roundRect", { x: 10.5, y: 3.4, w: 2.2, h: 0.95, rectRadius: 0.08, fill: { color: INK2 }, shadow: shadow() });
    s.addText("final_summary", { x: 10.5, y: 3.4, w: 2.2, h: 0.95, fontFace: H, fontSize: 12.5, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });

    // triggers card
    card(s, M, 4.75, 5.5, 1.95, AMBER);
    iconCircle(s, M + 0.26, 4.98, 0.56, AMBER, I.warn, 0.5);
    s.addText("Review is triggered when…", { x: M + 0.95, y: 4.95, w: 4.4, h: 0.4, fontFace: H, fontSize: 14, bold: true, color: INK, margin: 0 });
    s.addText([
      { text: "Overall risk is High or Critical", options: { bullet: true, breakLine: true } },
      { text: "Novel / divergent virus candidates exist", options: { bullet: true, breakLine: true } },
      { text: "A sample fails QC", options: { bullet: true } },
    ], { x: M + 0.95, y: 5.42, w: 4.4, h: 1.2, fontFace: B, fontSize: 12, color: SLATE, paraSpaceAfter: 4, margin: 0 });

    // error guard card
    card(s, 6.4, 4.75, W - M - 6.4, 1.95, CORAL);
    iconCircle(s, 6.66, 4.98, 0.56, CORAL, I.warn, 0.5);
    s.addText("Error handling (any node)", { x: 7.35, y: 4.95, w: 5.0, h: 0.4, fontFace: H, fontSize: 14, bold: true, color: INK, margin: 0 });
    s.addText([
      { text: "Critical error → error_handler classifies severity", options: { bullet: true, breakLine: true } },
      { text: "Recoverable → best-effort report; fatal → safe stop", options: { bullet: true, breakLine: true } },
      { text: "All errors logged — no silent failures", options: { bullet: true } },
    ], { x: 7.35, y: 5.42, w: 5.4, h: 1.2, fontFace: B, fontSize: 12, color: SLATE, paraSpaceAfter: 4, margin: 0 });
  }

  // ---------- 8. SHARED STATE ----------
  {
    const s = pres.addSlide();
    lightHeader(s, "Data model", "Shared state: one structure flows through all nodes", 8);
    // left: concept
    card(s, M, 1.95, 6.1, 4.7, TEAL);
    iconCircle(s, M + 0.34, 2.25, 0.8, TEAL, I.cubes, 0.5);
    s.addText("MetaMAVSState", { x: M + 1.3, y: 2.32, w: 4.6, h: 0.5, fontFace: H, fontSize: 19, bold: true, color: INK, margin: 0 });
    s.addText("A TypedDict every node reads & partially updates.", { x: M + 1.3, y: 2.78, w: 4.6, h: 0.4, fontFace: B, fontSize: 12.5, color: SLATE, margin: 0 });
    s.addText([
      { text: "Most fields: last-write-wins (LangGraph default)", options: { bullet: true, breakLine: true } },
      { text: "warnings / errors / execution_log use add-reducers", options: { bullet: true, breakLine: true } },
      { text: "→ each node returns only its NEW items; appended automatically", options: { bullet: true, indentLevel: 1, breakLine: true } },
      { text: "create_initial_state() seeds sensible defaults", options: { bullet: true, breakLine: true } },
      { text: "No hidden global state — everything is explicit", options: { bullet: true } },
    ], { x: M + 0.4, y: 3.5, w: 5.4, h: 3.0, fontFace: B, fontSize: 13, color: DARK, paraSpaceAfter: 7, margin: 0 });

    // right: code-ish snippet
    s.addShape("rect", { x: 7.0, y: 1.95, w: W - M - 7.0, h: 4.7, fill: { color: INK }, shadow: shadow() });
    s.addShape("rect", { x: 7.0, y: 1.95, w: W - M - 7.0, h: 0.45, fill: { color: INK2 } });
    s.addText("state.py", { x: 7.2, y: 1.95, w: 4, h: 0.45, fontFace: "Consolas", fontSize: 12, bold: true, color: MINT, valign: "middle", margin: 0 });
    s.addText([
      { text: "class MetaMAVSState(TypedDict, total=False):", options: { color: "8AD9D2", breakLine: true } },
      { text: "    config: dict", options: { color: "D7E3EA", breakLine: true } },
      { text: "    run_id: str", options: { color: "D7E3EA", breakLine: true } },
      { text: "    qc_pass_fail: dict", options: { color: "D7E3EA", breakLine: true } },
      { text: "    risk_summary: dict", options: { color: "D7E3EA", breakLine: true } },
      { text: "    review_required: bool", options: { color: "D7E3EA", breakLine: true } },
      { text: "    markdown_report_path: str | None", options: { color: "D7E3EA", breakLine: true } },
      { text: "    warnings:  Annotated[list, add]", options: { color: "F4C77B", breakLine: true } },
      { text: "    errors:    Annotated[list, add]", options: { color: "F4C77B", breakLine: true } },
      { text: "    execution_log: Annotated[list, add]", options: { color: "F4C77B", breakLine: true } },
      { text: "    workflow_status: str", options: { color: "D7E3EA" } },
    ], { x: 7.25, y: 2.6, w: W - M - 7.3, h: 3.9, fontFace: "Consolas", fontSize: 12.5, color: "D7E3EA", lineSpacingMultiple: 1.12, margin: 0 });
  }

  // ---------- 9. TECH FRAMEWORK & LAYERING ----------
  {
    const s = pres.addSlide();
    lightHeader(s, "Stack", "Framework & layering — LangGraph is the only framework", 9);
    const layers = [
      ["Orchestration / Framework", "LangGraph StateGraph — nodes, conditional edges, checkpoint, HITL, error routing", TEAL, "diagram"],
      ["Node / Business", "agents/*.py — 12 agents, pure functions (state) → partial dict", AMBER, "robot"],
      ["Utility / Infrastructure", "logging · files · command_runner · taxonomy · report rendering", INK2, "gears"],
      ["Data validation", "config.py + schemas.py (pydantic) — validates config & manifest only", MINT, "clip"],
    ];
    let y = 1.95; const h = 0.92, g = 0.14;
    layers.forEach((l) => {
      card(s, M, y, 7.7, h, l[2]);
      iconCircle(s, M + 0.24, y + 0.16, 0.6, l[2], I[l[3]], 0.5);
      s.addText(l[0], { x: M + 1.05, y: y + 0.1, w: 3.0, h: h - 0.2, fontFace: H, fontSize: 13.5, bold: true, color: INK, valign: "middle", margin: 0 });
      s.addText(l[1], { x: M + 4.0, y: y + 0.1, w: 3.6, h: h - 0.2, fontFace: B, fontSize: 11, color: SLATE, valign: "middle", lineSpacingMultiple: 1.04, margin: 0 });
      y += h + g;
    });
    // right: library roles
    const rx = 8.6, rw = W - M - 8.6;
    s.addShape("rect", { x: rx, y: 1.95, w: rw, h: 4.42, fill: { color: WHITE }, line: { color: LINE, width: 1 }, shadow: shadow() });
    s.addShape("rect", { x: rx, y: 1.95, w: rw, h: 0.5, fill: { color: INK } });
    s.addText("Library roles", { x: rx + 0.2, y: 1.95, w: rw - 0.4, h: 0.5, fontFace: H, fontSize: 13.5, bold: true, color: WHITE, valign: "middle", margin: 0 });
    const libs = [
      ["LangGraph", "the framework ✔"],
      ["pydantic", "data validation"],
      ["pandas", "tables / CSV"],
      ["PyYAML", "config parsing"],
      ["typer", "CLI"],
      ["pytest", "tests"],
      ["LangChain", "Phase 4 only — unused"],
    ];
    let ly = 2.62;
    libs.forEach((lb, i) => {
      const accent = i === 0 ? TEAL : SLATE;
      s.addShape("oval", { x: rx + 0.22, y: ly + 0.04, w: 0.13, h: 0.13, fill: { color: accent } });
      s.addText([
        { text: lb[0] + "  ", options: { bold: true, color: i === 0 ? TEAL : INK } },
        { text: "— " + lb[1], options: { color: SLATE } },
      ], { x: rx + 0.45, y: ly - 0.06, w: rw - 0.6, h: 0.34, fontFace: B, fontSize: 11.5, margin: 0 });
      ly += 0.5;
    });
  }

  // ---------- 10. ROADMAP ----------
  {
    const s = pres.addSlide();
    darkBase(s);
    s.addText("ROADMAP", { x: M, y: 0.6, w: 8, h: 0.3, fontFace: H, fontSize: 12, bold: true, color: MINT, charSpacing: 3, margin: 0 });
    s.addText("Four phases — incremental delivery", { x: M, y: 0.88, w: W - 2 * M, h: 0.6, fontFace: H, fontSize: 28, bold: true, color: WHITE, margin: 0 });
    const phases = [
      ["Phase 1", "Minimal Prototype", "Deterministic dry-run of the full LangGraph flow + reports + tests.", MINT, "DONE"],
      ["Phase 2", "Real Execution", "Run generated commands; tool checks, exit codes, recovery, SLURM.", TEAL, "NEXT"],
      ["Phase 3", "Bioinformatics", "Integrate real tools (Kraken2, DIAMOND, MEGAHIT, VirSorter2…).", "3E6E8E", "PLANNED"],
      ["Phase 4", "LLM Interpretation", "Optional LLM reasoning in nodes — interpretation, narrative, prose.", "5B5A8E", "PLANNED"],
    ];
    const cw = (W - 2 * M - 3 * 0.4) / 4, y = 2.0, ch = 3.9;
    phases.forEach((p, i) => {
      const x = M + i * (cw + 0.4);
      s.addShape("rect", { x, y, w: cw, h: ch, fill: { color: INK2 }, shadow: shadow() });
      s.addShape("rect", { x, y, w: cw, h: 0.14, fill: { color: p[3] } });
      // status pill
      const pill = p[4] === "DONE" ? MINT : p[4] === "NEXT" ? AMBER : "2C4A5E";
      s.addShape("roundRect", { x: x + 0.3, y: y + 0.4, w: 1.7, h: 0.42, rectRadius: 0.21, fill: { color: pill } });
      s.addText(p[4], { x: x + 0.3, y: y + 0.4, w: 1.7, h: 0.42, fontFace: H, fontSize: 11, bold: true, color: p[4] === "PLANNED" ? "9FB3C0" : INK, align: "center", valign: "middle", margin: 0 });
      s.addText(p[0], { x: x + 0.3, y: y + 1.0, w: cw - 0.6, h: 0.5, fontFace: H, fontSize: 22, bold: true, color: WHITE, margin: 0 });
      s.addText(p[1], { x: x + 0.3, y: y + 1.55, w: cw - 0.6, h: 0.5, fontFace: H, fontSize: 14, bold: true, color: p[3], margin: 0 });
      s.addText(p[2], { x: x + 0.3, y: y + 2.15, w: cw - 0.6, h: 1.5, fontFace: B, fontSize: 12, color: "9FB3C0", lineSpacingMultiple: 1.15, margin: 0 });
    });
    s.addText("Each phase stays runnable; later phases never require rewriting earlier ones.  No LLM API key needed for Phases 1–3.",
      { x: M, y: 6.3, w: W - 2 * M, h: 0.5, fontFace: B, fontSize: 13, italic: true, color: "BFE9E6", align: "center", margin: 0 });
  }

  // ---------- 11. PHASE 1 DELIVERED ----------
  {
    const s = pres.addSlide();
    lightHeader(s, "Status", "Phase 1 — delivered & verified", 11);
    // stat callouts
    const stats = [["37", "tests passing"], ["12", "agent nodes"], ["4", "CLI commands"], ["0", "API keys needed"]];
    const sw = (W - 2 * M - 3 * 0.4) / 4, sy = 1.9, sh = 1.5;
    stats.forEach((st, i) => {
      const x = M + i * (sw + 0.4);
      s.addShape("rect", { x, y: sy, w: sw, h: sh, fill: { color: INK }, shadow: shadow() });
      s.addShape("rect", { x, y: sy, w: sw, h: 0.1, fill: { color: MINT } });
      s.addText(st[0], { x, y: sy + 0.2, w: sw, h: 0.8, fontFace: H, fontSize: 44, bold: true, color: MINT, align: "center", margin: 0 });
      s.addText(st[1], { x, y: sy + 1.05, w: sw, h: 0.35, fontFace: B, fontSize: 12, color: "BFE9E6", align: "center", margin: 0 });
    });
    // checklist
    const items = [
      "Full project skeleton + pydantic config + manifest validation",
      "LangGraph StateGraph builds, compiles & runs end-to-end",
      "All 12 nodes execute; conditional review routing works",
      "Dry-run command generation for every bioinformatics step",
      "Intermediate CSV/JSON + Markdown & HTML reports generated",
      "MemorySaver checkpointing; human-in-the-loop checkpoint",
    ];
    const cw = (W - 2 * M - 0.5) / 2, ch = 0.62, y0 = 3.7;
    items.forEach((it, i) => {
      const col = i % 2, row = Math.floor(i / 2);
      const x = M + col * (cw + 0.5), y = y0 + row * (ch + 0.2);
      s.addImage({ data: I.checkTeal, x: x, y: y + 0.06, w: 0.34, h: 0.34 });
      s.addText(it, { x: x + 0.5, y: y, w: cw - 0.5, h: ch, fontFace: B, fontSize: 12.5, color: DARK, valign: "middle", lineSpacingMultiple: 1.0, margin: 0 });
    });
    s.addText("metamavs run --config configs/example_config.yaml --dry-run   →   completed_with_warnings",
      { x: M, y: 6.55, w: W - 2 * M, h: 0.4, fontFace: "Consolas", fontSize: 11.5, color: TEALD, align: "center", margin: 0 });
  }

  // ---------- 12. WHAT A RUN PRODUCES ----------
  {
    const s = pres.addSlide();
    lightHeader(s, "Output", "What a run produces", 12);
    // left: run directory tree
    s.addShape("rect", { x: M, y: 1.95, w: 6.0, h: 4.7, fill: { color: INK }, shadow: shadow() });
    s.addShape("rect", { x: M, y: 1.95, w: 6.0, h: 0.45, fill: { color: INK2 } });
    s.addText("reports/<run_name>/", { x: M + 0.2, y: 1.95, w: 5.6, h: 0.45, fontFace: "Consolas", fontSize: 12.5, bold: true, color: MINT, valign: "middle", margin: 0 });
    s.addText([
      { text: "logs/          metamavs.log, summaries", options: { breakLine: true } },
      { text: "intermediate/  validated manifest, JSON", options: { breakLine: true } },
      { text: "commands/      generated *.sh scripts", options: { breakLine: true } },
      { text: "tables/        hits, taxonomy, abundance,", options: { breakLine: true } },
      { text: "               trends, risk, novel (CSV)", options: { breakLine: true } },
      { text: "report.md      Markdown report", options: { breakLine: true, color: "8AD9D2" } },
      { text: "report.html    HTML report", options: { breakLine: true, color: "8AD9D2" } },
      { text: "state.json     complete final state", options: {} },
    ], { x: M + 0.25, y: 2.6, w: 5.6, h: 3.9, fontFace: "Consolas", fontSize: 12.5, color: "D7E3EA", lineSpacingMultiple: 1.18, margin: 0 });

    // right: example detections (the dry-run demo)
    s.addText("Example dry-run detections", { x: 7.0, y: 1.95, w: 5.6, h: 0.4, fontFace: H, fontSize: 15, bold: true, color: INK, margin: 0 });
    const rows = [
      ["SARS-CoV-2", "High", CORAL],
      ["Influenza A virus", "High", CORAL],
      ["Escherichia phage T4", "Low (phage)", TEAL],
      ["unclassified divergent RNA virus", "Novel candidate", AMBER],
      ["low-complexity fragment", "Flagged FP", SLATE],
    ];
    let y = 2.5; const rw = W - M - 7.0, rh = 0.62;
    rows.forEach((r) => {
      s.addShape("rect", { x: 7.0, y, w: rw, h: rh, fill: { color: WHITE }, line: { color: LINE, width: 1 } });
      s.addShape("rect", { x: 7.0, y, w: 0.08, h: rh, fill: { color: r[2] } });
      s.addText(r[0], { x: 7.2, y, w: rw - 2.4, h: rh, fontFace: B, fontSize: 12, color: DARK, valign: "middle", margin: 0 });
      s.addShape("roundRect", { x: 7.0 + rw - 2.15, y: y + 0.13, w: 2.0, h: 0.36, rectRadius: 0.18, fill: { color: r[2] } });
      s.addText(r[1], { x: 7.0 + rw - 2.15, y: y + 0.13, w: 2.0, h: 0.36, fontFace: H, fontSize: 10.5, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
      y += rh + 0.16;
    });
    s.addText("Synthetic data exercises every branch: risk escalation, phage flagging, novelty & human review.",
      { x: 7.0, y: y + 0.05, w: rw, h: 0.7, fontFace: B, fontSize: 11.5, italic: true, color: SLATE, lineSpacingMultiple: 1.1, margin: 0 });
  }

  // ---------- 13. HOW TO RUN ----------
  {
    const s = pres.addSlide();
    darkBase(s);
    s.addText("GET STARTED", { x: M, y: 0.6, w: 8, h: 0.3, fontFace: H, fontSize: 12, bold: true, color: MINT, charSpacing: 3, margin: 0 });
    s.addText("How to run it", { x: M, y: 0.88, w: W - 2 * M, h: 0.6, fontFace: H, fontSize: 28, bold: true, color: WHITE, margin: 0 });
    const blocks = [
      ["terminal", "Install", "pip install -e \".[dev]\""],
      ["diagram", "Inspect the graph", "metamavs graph --config configs/example_config.yaml"],
      ["check", "Validate inputs", "metamavs validate --config configs/example_config.yaml"],
      ["robot", "Run (dry-run)", "metamavs run --config configs/example_config.yaml --dry-run"],
      ["clip", "Test", "pytest    # 37 passing"],
    ];
    let y = 2.0; const h = 0.86, g = 0.16;
    blocks.forEach((bk) => {
      s.addShape("rect", { x: M, y, w: W - 2 * M, h, fill: { color: INK2 }, shadow: shadow() });
      iconCircle(s, M + 0.22, y + 0.16, 0.54, TEAL, I[bk[0]], 0.5);
      s.addText(bk[1], { x: M + 1.0, y, w: 2.7, h, fontFace: H, fontSize: 14.5, bold: true, color: WHITE, valign: "middle", margin: 0 });
      s.addText(bk[2], { x: M + 3.8, y, w: W - 2 * M - 4.0, h, fontFace: "Consolas", fontSize: 13.5, color: MINT, valign: "middle", margin: 0 });
      y += h + g;
    });
  }

  // ---------- 14. CLOSING ----------
  {
    const s = pres.addSlide();
    s.background = { color: INK };
    s.addShape("rect", { x: 0, y: 0, w: W, h: 0.12, fill: { color: TEAL } });
    s.addShape("rect", { x: 0, y: 0, w: 4.4, h: 0.12, fill: { color: MINT } });
    iconCircle(s, M, 1.5, 1.0, TEAL, I.virus, 0.5);
    s.addText("MetaMAVS in one line", { x: M, y: 2.7, w: 11, h: 0.5, fontFace: H, fontSize: 16, bold: true, color: MINT, margin: 0 });
    s.addText("A LangGraph multi-agent virus-surveillance workflow — deterministic today, LLM-ready tomorrow.",
      { x: M, y: 3.15, w: 11.6, h: 1.1, fontFace: H, fontSize: 30, bold: true, color: WHITE, lineSpacingMultiple: 1.05, margin: 0 });
    // takeaways
    const t = [
      ["check", "Phase 1 delivered: 12 nodes, routing, HITL, reports, 37 tests"],
      ["list", "4-phase roadmap; each phase stays runnable"],
      ["layer", "LangGraph is the sole framework; scientific caution throughout"],
    ];
    let y = 4.55;
    t.forEach((it) => {
      s.addImage({ data: I.check, x: M, y: y + 0.02, w: 0.32, h: 0.32 });
      s.addText(it[1], { x: M + 0.5, y, w: 11, h: 0.4, fontFace: B, fontSize: 14, color: "BFE9E6", valign: "middle", margin: 0 });
      y += 0.5;
    });
    s.addShape("rect", { x: M, y: 6.5, w: W - 2 * M, h: 0.5, fill: { color: INK2 } });
    s.addText([
      { text: "Repository:  ", options: { bold: true, color: WHITE } },
      { text: "github.com/pengsihua2023/MetaMAVS", options: { color: MINT } },
    ], { x: M + 0.2, y: 6.5, w: W - 2 * M - 0.4, h: 0.5, fontFace: B, fontSize: 14, valign: "middle", margin: 0 });
  }

  await pres.writeFile({ fileName: "MetaMAVS_Team_Intro.pptx" });
  console.log("WROTE MetaMAVS_Team_Intro.pptx");
}

build().catch((e) => { console.error(e); process.exit(1); });
