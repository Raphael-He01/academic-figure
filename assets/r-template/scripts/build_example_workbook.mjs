import fs from "node:fs/promises";
import { existsSync } from "node:fs";
import os from "node:os";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);
let artifactToolEntry;
try {
  artifactToolEntry = require.resolve("@oai/artifact-tool");
} catch {
  const runtimeNodeModules = process.env.CODEX_NODE_MODULES ?? path.join(
    os.homedir(),
    ".cache",
    "codex-runtimes",
    "codex-primary-runtime",
    "dependencies",
    "node",
    "node_modules",
  );
  if (!existsSync(runtimeNodeModules)) {
    throw new Error(
      "Cannot find @oai/artifact-tool. Run this script inside Codex or set " +
      "CODEX_NODE_MODULES to the bundled node_modules directory.",
    );
  }
  artifactToolEntry = require.resolve("@oai/artifact-tool", {
    paths: [runtimeNodeModules],
  });
}
const { FileBlob, SpreadsheetFile, Workbook } = await import(
  pathToFileURL(artifactToolEntry).href
);

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(scriptDir, "..");
const outputDir = path.join(projectRoot, "output", "spreadsheet");
const previewDir = path.join(outputDir, "previews");
await fs.mkdir(previewDir, { recursive: true });

const workbook = Workbook.create();
const fontFamily = "Arial";
const headerFill = "#263746";
const headerText = "#FFFFFF";
const ruleColor = "#CBD2D9";
const titleColor = "#1F2933";

function columnLetters(count) {
  const result = [];
  for (let n = 1; n <= count; n += 1) {
    let value = n;
    let letters = "";
    while (value > 0) {
      value -= 1;
      letters = String.fromCharCode(65 + (value % 26)) + letters;
      value = Math.floor(value / 26);
    }
    result.push(letters);
  }
  return result;
}

function styleTableSheet(sheet, rows, cols, tableName) {
  const lastCol = columnLetters(cols).at(-1);
  const used = sheet.getRange(`A1:${lastCol}${rows}`);
  used.format.font = { name: fontFamily, size: 10, color: titleColor };
  used.format.verticalAlignment = "center";

  const header = sheet.getRange(`A1:${lastCol}1`);
  header.format = {
    fill: headerFill,
    font: { name: fontFamily, size: 10, bold: true, color: headerText },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    borders: { preset: "outside", style: "thin", color: headerFill },
  };
  header.format.rowHeight = 24;

  if (rows > 1) {
    sheet.getRange(`A2:${lastCol}${rows}`).format.borders = {
      insideHorizontal: { style: "thin", color: ruleColor },
    };
  }
  sheet.tables.add(`A1:${lastCol}${rows}`, true, tableName);
  sheet.freezePanes.freezeRows(1);
  sheet.showGridLines = false;
}

function convertTypes(values, numericColumns = [], booleanColumns = []) {
  const headers = values[0];
  const numericIndexes = numericColumns.map((name) => headers.indexOf(name));
  const booleanIndexes = booleanColumns.map((name) => headers.indexOf(name));
  return values.map((row, rowIndex) => {
    if (rowIndex === 0) return row;
    return row.map((value, columnIndex) => {
      if (numericIndexes.includes(columnIndex)) {
        return value === "" ? null : Number(value);
      }
      if (booleanIndexes.includes(columnIndex)) {
        if (value === "TRUE" || value === "true") return true;
        if (value === "FALSE" || value === "false") return false;
      }
      return value;
    });
  });
}

async function addCsvSheet({
  csvName,
  sheetName,
  tableName,
  numericColumns = [],
  booleanColumns = [],
  widths = [],
  numberFormats = {},
}) {
  const csvPath = path.join(projectRoot, "data", csvName);
  const csvText = await fs.readFile(csvPath, "utf8");
  const csvWorkbook = await Workbook.fromCSV(csvText, { sheetName });
  const csvSheet = csvWorkbook.worksheets.getItem(sheetName);
  const imported = csvSheet.getUsedRange().values;
  const values = convertTypes(imported, numericColumns, booleanColumns);

  const sheet = workbook.worksheets.add(sheetName);
  sheet.getRange("A1").write(values);
  styleTableSheet(sheet, values.length, values[0].length, tableName);

  const columns = columnLetters(values[0].length);
  widths.forEach((width, index) => {
    if (width) sheet.getRange(`${columns[index]}1:${columns[index]}${values.length}`).format.columnWidth = width;
  });
  for (const [columnName, formatCode] of Object.entries(numberFormats)) {
    const index = values[0].indexOf(columnName);
    if (index >= 0 && values.length > 1) {
      sheet.getRange(`${columns[index]}2:${columns[index]}${values.length}`).format.numberFormat = formatCode;
    }
  }
  return sheet;
}

const metadata = workbook.worksheets.add("Metadata");
metadata.getRange("A1:B11").values = [
  ["Field", "Value"],
  ["Dataset", "Academic figure workflow example"],
  ["Status", "SIMULATED DATA - not a real scientific result"],
  ["Random seed", 20261009],
  ["Generated date", "2026-10-09"],
  ["Primary analysis", "R 4.6.1 with a project-local renv environment"],
  ["Group order", "Control | Treatment A | Treatment B"],
  ["Response unit", "a.u. (arbitrary units)"],
  ["Missing values", "Blank cells; never interpret a blank as zero"],
  ["Precision", "Source values retain three decimals; plot labels use task-appropriate precision"],
  ["Origin handoff", "Import worksheet data, not exported figure images, to retain editable data bindings"],
];
styleTableSheet(metadata, 11, 2, "MetadataTable");
metadata.getRange("A1:A11").format.columnWidth = 22;
metadata.getRange("B1:B11").format.columnWidth = 78;
metadata.getRange("B2:B11").format.wrapText = true;
metadata.getRange("B2:B11").format.rowHeight = 30;
metadata.tabColor = "#263746";

const levels = workbook.worksheets.add("Levels");
levels.getRange("A1:G10").values = [
  ["variable", "level", "order", "display_label", "color_hex", "R_shape", "R_linetype"],
  ["group", "Control", 1, "Control", "#222222", 16, "solid"],
  ["group", "Treatment A", 2, "Treatment A", "#0072B2", 17, "longdash"],
  ["group", "Treatment B", 3, "Treatment B", "#E69F00", 15, "dotted"],
  ["condition", "Control_D7", 1, "Control D7", null, null, null],
  ["condition", "TreatmentA_D7", 2, "Treatment A D7", null, null, null],
  ["condition", "TreatmentB_D7", 3, "Treatment B D7", null, null, null],
  ["condition", "Control_D28", 4, "Control D28", null, null, null],
  ["condition", "TreatmentA_D28", 5, "Treatment A D28", null, null, null],
  ["condition", "TreatmentB_D28", 6, "Treatment B D28", null, null, null],
];
styleTableSheet(levels, 10, 7, "LevelsTable");
levels.getRange("A1:B10").format.columnWidth = 22;
levels.getRange("C1:C10").format.columnWidth = 11;
levels.getRange("D1:D10").format.columnWidth = 23;
levels.getRange("E1:G10").format.columnWidth = 14;
levels.getRange("C2:C10").format.numberFormat = "0";
levels.getRange("F2:F10").format.numberFormat = "0";
levels.tabColor = "#607D8B";

await addCsvSheet({
  csvName: "simulated_trend.csv",
  sheetName: "Trend",
  tableName: "TrendData",
  numericColumns: ["day", "replicate", "response", "simulation_seed"],
  booleanColumns: ["is_simulated"],
  widths: [10, 19, 12, 15, 17, 16, 20],
  numberFormats: { day: "0", replicate: "0", response: "0.000", simulation_seed: "0" },
});

await addCsvSheet({
  csvName: "simulated_distribution.csv",
  sheetName: "Distribution",
  tableName: "DistributionData",
  numericColumns: ["day", "replicate", "response", "simulation_seed"],
  booleanColumns: ["is_simulated"],
  widths: [10, 19, 12, 15, 17, 16, 20],
  numberFormats: { day: "0", replicate: "0", response: "0.000", simulation_seed: "0" },
});

await addCsvSheet({
  csvName: "simulated_heatmap.csv",
  sheetName: "Heatmap",
  tableName: "HeatmapData",
  numericColumns: ["z_score", "simulation_seed"],
  booleanColumns: ["is_simulated"],
  widths: [16, 24, 14, 13, 16, 20],
  numberFormats: { z_score: "0.000", simulation_seed: "0" },
});

await addCsvSheet({
  csvName: "simulated_data_dictionary.csv",
  sheetName: "Dictionary",
  tableName: "DataDictionary",
  widths: [30, 22, 19, 14, 72],
});
const dictionary = workbook.worksheets.getItem("Dictionary");
dictionary.getRange("E2:E21").format.wrapText = true;
dictionary.getRange("E2:E21").format.rowHeight = 30;

workbook.recalculate();

const keyInspection = await workbook.inspect({
  kind: "table",
  range: "Metadata!A1:B11",
  include: "values,formulas",
  tableMaxRows: 15,
  tableMaxCols: 8,
});
console.log(keyInspection.ndjson);

const errorScan = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 100 },
  summary: "final formula error scan",
});
console.log(errorScan.ndjson);

for (const sheetName of ["Metadata", "Levels", "Trend", "Distribution", "Heatmap", "Dictionary"]) {
  const preview = await workbook.render({
    sheetName,
    autoCrop: "all",
    scale: 1.25,
    format: "png",
  });
  await fs.writeFile(
    path.join(previewDir, `${sheetName.toLowerCase()}.png`),
    new Uint8Array(await preview.arrayBuffer()),
  );
}

const outputPath = path.join(outputDir, "simulated_academic_figure_data.xlsx");
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);

const reopened = await SpreadsheetFile.importXlsx(await FileBlob.load(outputPath));
const reopenedInspection = await reopened.inspect({
  kind: "sheet",
  include: "id,name",
  maxChars: 4000,
});
console.log(reopenedInspection.ndjson);
await fs.rm(`${outputPath}.inspect.ndjson`, { force: true });
console.log(`Workbook saved: ${outputPath}`);
