import { requestAdminApi, type ReadAdminResourceOptions } from "./client";

export const usersApi = {
  list: (options?: ReadAdminResourceOptions) =>
    requestAdminApi(["users"], { ...options, trailingSlash: true }),
};
