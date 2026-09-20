import type { Product } from "../types/chat";
import { formatPrice } from "../utils/format";

interface ProductCardProps {
  product: Product;
}

export function ProductCard({ product }: ProductCardProps) {
  const hasDiscount = product.originalPrice > product.price;

  return (
    <article className="product-card">
      {(product.isBestSeller || product.isNew) && (
        <div className="product-card__badges">
          {product.isBestSeller && (
            <span className="badge badge--bestseller">Best Seller</span>
          )}
          {product.isNew && <span className="badge badge--new">New</span>}
        </div>
      )}

      <p className="product-card__brand">{product.brand}</p>
      <h3 className="product-card__name">{product.name}</h3>

      <div className="product-card__price">
        <span className="product-card__price-current">
          {formatPrice(product.price, product.currency)}
        </span>
        {hasDiscount && (
          <span className="product-card__price-original">
            {formatPrice(product.originalPrice, product.currency)}
          </span>
        )}
      </div>

      <div className="product-card__rating">
        <span aria-hidden="true">★</span>
        <span>{product.rating.toFixed(1)}</span>
        <span className="product-card__reviews">
          ({product.reviewCount} reviews)
        </span>
      </div>

      <p className="product-card__meta">
        {product.sport} · {product.category}
      </p>

      <p
        className={
          product.inStock
            ? "product-card__stock product-card__stock--in"
            : "product-card__stock product-card__stock--out"
        }
      >
        {product.inStock ? "In stock" : "Out of stock"}
      </p>

      {product.description && (
        <p className="product-card__description">{product.description}</p>
      )}
    </article>
  );
}
