#!/usr/bin/env bun
/**
 * Stop hook: keeps a Worker Agent iterating while the TDD loop is still red.
 * Emits { continue: true, reason } to resume, or { continue: false } to stop.
 */
import { spawnSync } from "node:child_process";
import { existsSync, readFileSync, writeFileSync, mkdirSync } from "node:fs";

const STATE_FILE = ".cursor/.grind-state.json";
const MAX_ITERATIONS = 12;

type State = { iterations: number };

function loadState(): State {
  if (!existsSync(STATE_FILE)) return { iterations: 0 };
  try {
    return JSON.parse(readFileSync(STATE_FILE, "utf8")) as State;
  } catch {
    return { iterations: 0 };
  }
}

function saveState(state: State): void {
  mkdirSync(".cursor", { recursive: true });
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

function run(cmd: string, args: string[]) {
  return spawnSync(cmd, args, { encoding: "utf8", stdio: "pipe" });
}

/** Test commands for every stack actually present in the repo. */
function testCommands(): Array<{ label: string; cmd: string; args: string[] }> {
  const commands: Array<{ label: string; cmd: string; args: string[] }> = [];
  if (existsSync("tests") || existsSync("pyproject.toml") || existsSync("requirements.txt")) {
    commands.push({ label: "pytest", cmd: "pytest", args: ["-q"] });
  }
  if (existsSync("package.json")) {
    commands.push({ label: "npm test", cmd: "npm", args: ["run", "test", "--silent"] });
  }
  if (existsSync("pubspec.yaml")) {
    commands.push({ label: "flutter test", cmd: "flutter", args: ["test"] });
  }
  return commands;
}

function emit(shouldContinue: boolean, reason: string): never {
  console.log(JSON.stringify({ continue: shouldContinue, reason }));
  process.exit(0);
}

const state = loadState();
const commands = testCommands();

if (commands.length === 0) {
  emit(false, "No test harness detected; nothing to grind.");
}

const failures: string[] = [];
for (const { label, cmd, args } of commands) {
  const result = run(cmd, args);
  if (result.error) continue; // Toolchain absent — not a red test.
  if (result.status !== 0) {
    failures.push(`${label}: ${(result.stderr || result.stdout || "").trim().slice(-800)}`);
  }
}

if (failures.length === 0) {
  saveState({ iterations: 0 });
  emit(false, "All detected test suites are green. TDD loop complete.");
}

state.iterations += 1;
saveState(state);

if (state.iterations >= MAX_ITERATIONS) {
  saveState({ iterations: 0 });
  emit(false, `Stopping after ${MAX_ITERATIONS} iterations with tests still red. Human review required.`);
}

emit(
  true,
  `Tests still red (iteration ${state.iterations}/${MAX_ITERATIONS}). ` +
    `Fix implementation code only. Keep red tests unchanged; use the test guard where supported.\n\n${failures.join("\n\n")}`,
);
