import { defineCollection, z } from 'astro:content';

const docsCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
    date: z.union([z.string(), z.date()]).optional(),
    category: z.string().optional(),
  }),
});

export const collections = {
  'docs': docsCollection,
};