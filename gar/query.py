sql_find_child = """
select
    o1.object_id as address_objects,
    o2.object_id as houses,
    o3.object_id as apartments
from {hierarchy_table} h
    left join address_objects o1 on o1.object_id = h.object_id
    left join houses o2 on o2.object_id = h.object_id and (:add_num1 is null or o2.add_num1 = :add_num1) and (:add_num2 is null or o2.add_num2 = :add_num2)
    left join apartments o3 on o3.object_id = h.object_id
where (h.parent_object_id = :object_id or (:object_id is null and h.parent_object_id is null))
    and (o1.name like :text or o2.house_num like :text or o3.number like :text)
order by h.is_active desc, 
    o1.name, o2.house_num, o3.number,
    h.start_date desc,
    o1.is_active desc, o1.start_date desc, 
    o2.is_active desc, o2.start_date desc, 
    o3.is_active desc, o3.start_date desc
limit :limit;
"""
