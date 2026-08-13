import assert from "node:assert/strict";
import test from "node:test";
import { HttpError } from "@/lib/http";

test("HttpError preserves status and safe message", () => {
  const error = new HttpError(409, "Git base changed");
  assert.equal(error.status, 409);
  assert.equal(error.message, "Git base changed");
});
