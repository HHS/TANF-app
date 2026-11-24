import { requestAdminApi, type ReadAdminResourceOptions } from "./client";

export const usersApi = {
  list: (options?: ReadAdminResourceOptions) =>
    requestAdminApi(["users"], { ...options, trailingSlash: true }),
  get: (id: string, options?: ReadAdminResourceOptions) =>
    requestAdminApi(["users", id], { ...options, trailingSlash: true }),
  summary: (options?: ReadAdminResourceOptions) =>
    requestAdminApi(["users", "summary"], { ...options, trailingSlash: true }),
};
