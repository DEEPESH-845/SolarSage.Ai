import { describe, expect, it } from "vitest";
import { decimal, ml, pct, pctWhole, reading, stamp, titleCase, words } from "../format";

/**
 * These run on every value the backend can send, including the nulls. A panel
 * that has never been analysed has no dust level, and the console must print
 * that as an em dash rather than "NaN%" — which is the bug these guard.
 */
describe("format", () => {
  it("prints a fraction as a percentage", () => {
    expect(pct(0.2307)).toBe("23.1%");
    expect(pct(0.2307, 2)).toBe("23.07%");
    expect(pctWhole(0.66)).toBe("66%");
  });

  it("prints an em dash for a missing reading", () => {
    expect(pct(null)).toBe("—");
    expect(pct(undefined)).toBe("—");
    expect(pctWhole(null)).toBe("—");
    expect(ml(null)).toBe("—");
  });

  it("rounds millilitres and groups them", () => {
    expect(ml(100)).toBe("100 ml");
    expect(ml(1234.6)).toBe("1,235 ml");
  });

  it("trims a timestamp to the second and drops the T", () => {
    expect(stamp("2026-08-20T03:11:46.310000")).toBe("2026-08-20 03:11:46");
    expect(stamp(null)).toBe("never");
    expect(stamp(null, "")).toBe("");
  });

  it("turns snake_case into words", () => {
    expect(words("needs_cleaning")).toBe("needs cleaning");
    expect(titleCase("needs_cleaning")).toBe("Needs Cleaning");
    // The forecaster shouts its enums; the console never did.
    expect(titleCase("WITHIN_24H")).toBe("Within 24h");
    expect(titleCase(null)).toBe("");
  });

  it("prints a whole reading the way the service layer prints it", () => {
    // Python sends 81.0 and JSON delivers 81; the column has always read "81.0%".
    expect(reading(81, "%")).toBe("81.0%");
    expect(reading(83.1, "%")).toBe("83.1%");
    expect(reading(null)).toBe("—");
  });

  it("keeps the decimals a counter animates to", () => {
    expect(decimal(1234.5678, 2)).toBe("1,234.57");
    expect(decimal(1234.5678)).toBe("1,235");
  });
});
