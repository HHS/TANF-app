export * from "./admin-forms";
export * from "./client";
export * from "./data-files";
export * from "./users";

import { adminFormsApi } from "./admin-forms";
import { dataFilesApi } from "./data-files";
import { usersApi } from "./users";

export const adminApi = {
  adminForms: adminFormsApi,
  dataFiles: dataFilesApi,
  users: usersApi,
};
