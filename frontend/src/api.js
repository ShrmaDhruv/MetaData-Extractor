const normalizeBaseUrl = (value) => value.replace(/\/+$/, "");

const getDefaultBaseUrl = () => {
  if (typeof window === "undefined") return "";

  const { hostname, port } = window.location;
  const isLocalFrontend =
    ["localhost", "127.0.0.1"].includes(hostname) && port && port !== "8000";

  return isLocalFrontend ? "http://127.0.0.1:8000" : "";
};

const configuredBaseUrl =
  typeof process !== "undefined" && process.env
    ? process.env.API_BASE_URL || ""
    : "";

const API_BASE_URL = normalizeBaseUrl(configuredBaseUrl || getDefaultBaseUrl());

export const apiUrl = (path) => {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
};
