import { configureStore } from '@reduxjs/toolkit';
import { modelApi } from './modelService';  // Correct relative path

export const store = configureStore({
  reducer: {
    [modelApi.reducerPath]: modelApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(modelApi.middleware),
});
