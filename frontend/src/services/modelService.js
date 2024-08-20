import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

const apiToken = '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';

export const modelApi = createApi({
  reducerPath: 'modelApi',
  baseQuery: fetchBaseQuery({
    baseUrl: 'https://incletech-incle-sdg.hf.space/',
    prepareHeaders: (headers) => {
      headers.set('Authorization', `Bearer ${apiToken}`);
      headers.set('accept', 'application/json');
      return headers;
    },
  }),
  endpoints: (builder) => ({
    getModelCards: builder.query({
      query: () => 'get_model_card/',
    }),
    uploadFile: builder.mutation({
      query: ({ file, userId, model, modelProvider, outputFormat }) => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('user_id', userId);
        formData.append('model_providers', modelProvider);
        formData.append('model', model);
        formData.append('output_format', outputFormat); // Add output format

        return {
          url: 'upload-file/',
          method: 'POST',
          body: formData,
        };
      },
    }),
  }),
});

export const { useGetModelCardsQuery, useUploadFileMutation } = modelApi;
