import { requestAdminApi, type ReadAdminResourceOptions } from "./client";

export const dataFilesApi = {
  list: (options?: ReadAdminResourceOptions) =>
    requestAdminApi(["data_files"], options),
  get: (id: string | number, options?: ReadAdminResourceOptions) =>
    requestAdminApi(["data_files", String(id)], options),
};
