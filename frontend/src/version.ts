/**
 * Application version.
 * This value is injected at build time from the VERSION file.
 */
export const APP_VERSION = __APP_VERSION__;

/**
 * Get the application version.
 * @returns The current application version
 */
export function getVersion(): string {
  return APP_VERSION;
}
