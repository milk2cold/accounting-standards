import type { AstroIntegration } from "astro";
import type { RehypePlugin, RemarkPlugin } from "@astrojs/markdown-remark";
import { visit } from "unist-util-visit";

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\u4e00-\u9fa5]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

const remarkHeadingId: RemarkPlugin = () => {
  return (tree) => {
    visit(tree, "heading", (node) => {
      if (!node.data) node.data = {};
      if (!node.data.hProperties) node.data.hProperties = {};
      
      let text = "";
      visit(node, "text", (textNode) => {
        text += textNode.value;
      });
      
      if (text) {
        (node.data.hProperties as any).id = slugify(text);
      }
    });
  };
};

export default function markdownTransform(): AstroIntegration {
  return {
    name: "markdown-transform",
    hooks: {
      "astro:config:setup": ({ updateConfig }) => {
        updateConfig({
          markdown: {
            remarkPlugins: [remarkHeadingId],
          },
        });
      },
    },
  };
}
