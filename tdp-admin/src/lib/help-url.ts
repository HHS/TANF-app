const DEFAULT_HELP_URL = "http://localhost:3000/help/";

export function getHelpUrl(): string {
  const configuredUrl = process.env.TDP_HELP_URL?.trim() || DEFAULT_HELP_URL;
  return `${configuredUrl.replace(/\/+$/, "")}/`;
}

export function getKnowledgeCenterUrl(): string {
  return `${getHelpUrl()}knowledge-center/`;
}
