"""Services for asset sub-modules using a generic CRUD pattern."""

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.asset_modules import (
    ExternalBroadband,
    InterconnectIP,
    IPAllocation,
    IPPlan,
    LicenseManagement,
    PortConnection,
)
from app.services.audit_service import log_operation


class GenericCRUDService:
    """Generic CRUD service that works for any SQLAlchemy model with standard id/created_at/updated_at."""

    def __init__(self, model, search_fields=None, target_type=""):
        self.model = model
        self.search_fields = search_fields or []
        self.target_type = target_type or model.__tablename__

    def list(self, db, skip=0, limit=20, keyword=None, order="desc", **filters):
        query = db.query(self.model)
        if keyword and self.search_fields:
            query = query.filter(
                or_(*[getattr(self.model, f).ilike(f"%{keyword}%") for f in self.search_fields])
            )
        for key, val in filters.items():
            if val is not None and val != "":
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == val)
        total = query.count()
        order_col = self.model.id.desc() if order == "asc" else self.model.id.desc()
        if order == "asc":
            order_col = self.model.id.asc()
        items = query.order_by(order_col).offset(skip).limit(limit).all()
        return items, total

    def get_by_id(self, db, item_id):
        item = db.query(self.model).filter(self.model.id == item_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"记录不存在: id={item_id}")
        return item

    def create(self, db, item_create, operator, operator_ip):
        data = item_create.model_dump()
        # Resolve device names for FK fields
        self._resolve_names(db, data)
        # Auto-compute license status from activation/expiration dates
        if self.target_type == "license" and hasattr(self.model, "compute_status"):
            data["status"] = self.model.compute_status(
                activation_date=data.get("activation_date"),
                expiration_date=data.get("expiration_date"),
            )
        item = self.model(**data)
        db.add(item)
        db.commit()
        db.refresh(item)
        log_operation(db, operator=operator, operator_ip=operator_ip, operation_type="create",
                      target_type=self.target_type, target_id=item.id, result=True, detail=data)
        return item

    def update(self, db, item_id, item_update, operator, operator_ip):
        item = self.get_by_id(db, item_id)
        old_values = {}
        update_data = item_update.model_dump(exclude_unset=True)
        self._resolve_names(db, update_data)
        # Auto-compute license status when dates change
        if self.target_type == "license" and hasattr(self.model, "compute_status"):
            act = update_data.get("activation_date", old_values.get("activation_date"))
            exp = update_data.get("expiration_date", old_values.get("expiration_date"))
            update_data["status"] = self.model.compute_status(activation_date=act, expiration_date=exp)
        for field, value in update_data.items():
            old_values[field] = getattr(item, field)
            setattr(item, field, value)
        db.commit()
        db.refresh(item)
        log_operation(db, operator=operator, operator_ip=operator_ip, operation_type="update",
                      target_type=self.target_type, target_id=item.id, result=True,
                      detail={"old": old_values, "new": update_data})
        return item

    def delete(self, db, item_id, operator, operator_ip):
        item = self.get_by_id(db, item_id)
        db.delete(item)
        db.commit()
        log_operation(db, operator=operator, operator_ip=operator_ip, operation_type="delete",
                      target_type=self.target_type, target_id=item_id, result=True)
        return item

    def _resolve_names(self, db, data):
        """Auto-fill device_name fields from asset_id for FK-linked models."""
        from app.models.asset import Asset
        if "asset_id" in data and data["asset_id"]:
            asset = db.query(Asset).filter(Asset.id == data["asset_id"]).first()
            if asset:
                data["asset_name"] = asset.device_name
        if "source_device_id" in data and data["source_device_id"] is not None:
            asset = db.query(Asset).filter(Asset.id == data["source_device_id"]).first()
            if asset:
                data["source_device_name"] = asset.device_name
        if "dest_device_id" in data and data["dest_device_id"] is not None:
            asset = db.query(Asset).filter(Asset.id == data["dest_device_id"]).first()
            if asset:
                data["dest_device_name"] = asset.device_name

    def get_reverse_links(self, db, device_id, port_names):
        """For each port name in `port_names` of `device_id`, find a port on ANOTHER
        asset whose ports_data references (device_id, port_name) as its remote peer.
        Returns { port_name: {source asset + source port config} }.

        Used to auto-populate the reverse interconnection when opening the peer
        device's port-connection editor (e.g. A links to B.GE1 -> B.GE1 auto-links A).
        """
        from app.models.asset import Asset

        if not port_names:
            return {}
        nameset = {str(n).strip() for n in port_names}
        links = {}
        # Only meaningful for models that carry a ports_data JSON column.
        if not hasattr(self.model, "ports_data"):
            return links
        conns = db.query(self.model).all()
        for conn in conns:
            ports = getattr(conn, "ports_data", None) or []
            for p in ports:
                if not isinstance(p, dict):
                    continue
                cid = p.get("connected_device_id")
                cif = (p.get("connected_interface") or "").strip()
                if str(cid) == str(device_id) and cif in nameset and cif not in links:
                    asset = db.query(Asset).filter(Asset.id == conn.asset_id).first()
                    links[cif] = {
                        "source_asset_id": conn.asset_id,
                        "source_asset_name": asset.device_name if asset else "",
                        "source_port_name": p.get("name") or "",
                        "source_port_type": p.get("port_type") or "",
                        "source_net_type": p.get("net_type") or "",
                        "source_vlan_id": p.get("vlan_id") or "",
                        "source_vlan_range": p.get("vlan_range") or "",
                    }
        return links


# Service instances for each module
port_connection_service = GenericCRUDService(
    PortConnection,
    search_fields=["asset_name", "remark"],
    target_type="port_connection",
)

ip_plan_service = GenericCRUDService(
    IPPlan,
    search_fields=["ip_range", "department", "group_name", "vlan"],
    target_type="ip_plan",
)

interconnect_ip_service = GenericCRUDService(
    InterconnectIP,
    search_fields=["ip_range", "source_device_name", "dest_device_name"],
    target_type="interconnect_ip",
)

external_broadband_service = GenericCRUDService(
    ExternalBroadband,
    search_fields=["operator", "line_type", "ip_address", "ownership", "status"],
    target_type="external_broadband",
)

license_service = GenericCRUDService(
    LicenseManagement,
    search_fields=["brand", "device_name", "device_type"],
    target_type="license",
)

ip_allocation_service = GenericCRUDService(
    IPAllocation,
    search_fields=["department", "user_name", "ip_address", "registrar"],
    target_type="ip_allocation",
)
