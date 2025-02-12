from py4web import action, request, redirect, URL
from yatl.helpers import A, P
from .common import db, session, T, auth

from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.grid import Grid, GridClassStyleBulma

# Get index page (login page)

@action('index', method=["GET", "POST"])
@action.uses(db, auth.user, 'index.html')
def index():
    if request.method == 'GET':
        products = db(db.product.id > 0).select()
        invoices = db(db.output_invoice.id > 0).select()
        import_invoices = db(db.input_invoice.id > 0).select()
        return dict(products=products, invoices=invoices, import_invoices=import_invoices)


# Product management page - Using Py4web Grid

@action('product', method=["GET", "POST"])
@action('product/<path:path>', method=["GET", "POST"])
@action.uses(db, auth.user, 'product.html')
def product(path=None):

    raw_categories = db.executesql("SELECT * FROM categories;")
    categories = dict((y, x) for x, y in raw_categories)
    print(categories)
    grid = Grid(
        path, query=db.product.id > 0,
        search_form=None, editable=True, deletable=True, details=False, create=True,
        grid_class_style=GridClassStyleBulma, formstyle=FormStyleBulma, rows_per_page=4,
        search_queries=[
            ['By Code', lambda val: db.product.product_code.contains(val)],
            ['By Category', lambda val: db.product.categories_id == categories[str(val)]]
        ])
    #Count total product
    total = db(db.product.id > 0).select()
    return dict(grid=grid, total=len(total))

# Category Management Page - Using Py4web Grid
@action('category', method=["GET", "POST"])
@action('category/<path:path>', method=["GET", "POST"])
@action.uses(db, auth.user, 'category.html')
def category(path=None):

    grid = Grid(
        path,
        query=db.categories.id > 0,
        search_form=None,
        editable=True, deletable=True, details=False, create=True,
        grid_class_style=GridClassStyleBulma,
        formstyle=FormStyleBulma,
        search_queries=[
            ['By Name', lambda val: db.categories.name.contains(val)]])
    #Count total product
    total = db(db.categories.id > 0).select()

    return dict(grid=grid, total=len(total))


# User Management Page - Using Py4Web Grid
@action('user', method=["GET", "POST"])
@action('user/<path:path>', method=["GET", "POST"])
@action.uses(db, auth.user, 'user.html')
def user(path=None):

    grid = Grid(
        path,
        query=db.auth_user.id > 0,
        search_form=None,
        editable=True, deletable=True, details=False, create=True,
        grid_class_style=GridClassStyleBulma,
        formstyle=FormStyleBulma,
        search_queries=[
            ['By Username', lambda val: db.auth_user.username.contains(val)],
            ['By Email', lambda val: db.auth_user.email.contains(val)]])
    return dict(grid=grid)

# Get specific import invoice by id
@action('get-import-invoice/<invoice_id:int>', method=["GET"])
@action.uses(db, auth.user, 'import_invoice.html')
def get_import_invoice(invoice_id=None):

    if request.method == "GET":
        total = 0
        total_product = []

        invoice = db(db.input_invoice.id == invoice_id).select()

        invoice_details = db(
            db.input_invoice.id == db.input_invoice_details.input_invoice_id == invoice_id).select()

        products = db(db.product.id > 0).select()

        for i in invoice_details:
            total += int(i.total_price)
            total_product.append(i.product_id)

        return dict(invoice=invoice, invoice_details=invoice_details, total=total, products=products, total_products=len(total_product))

# Get specific export invoice with id
@action('get_invoice/<invoice_id:int>', method=["GET"])
@action.uses(db, auth.user, 'invoice.html')
def get_invoice(invoice_id=None):

    if request.method == "GET":
        total = 0
        total_product = []

        invoice = db(db.output_invoice.id == invoice_id).select()

        invoice_details = db(
            db.output_invoice.id == db.output_invoice_details.output_invoice_id == invoice_id).select()

        products = db(db.product.id > 0).select()

        for i in invoice_details:
            total += int(i.total_price)
            total_product.append(i.product_id)

        return dict(invoice=invoice, invoice_details=invoice_details, total=total, products=products, total_products=len(total_product))

# Create product in export in invoice
@action('post_invoice/<invoice_id:int>', method=["GET", "POST"])
@action.uses(db, auth.user, 'add.html')
def post_invoice(invoice_id=None):
    assert invoice_id is not None

    db.output_invoice_details.insert(
        output_invoice_id=invoice_id,
        product_id=request.params.get("productId"),
        quantity=int(request.params.get("quantity")),
        unit_price=int(request.params.get("unit_price"))
    )
   
  

    redirect(URL('get_invoice', invoice_id))

# Create product on import invoice
@action('post_import_invoice/<invoice_id:int>', method=["GET", "POST"])
@action.uses(db, auth.user, 'add.html')
def post_import_invoice(invoice_id=None):
    assert invoice_id is not None

    db.input_invoice_details.insert(
        input_invoice_id=invoice_id,
        product_id=request.params.get("productId"),
        quantity=int(request.params.get("quantity")),
        unit_price=int(request.params.get("unit_price"))
    )
   
  

    redirect(URL('get-import-invoice', invoice_id))


# Delete import invoice by id
@action('delete_import_invoice', method=["POST"])
@action.uses(db, auth.user)
def delete_import_invoice():
    if request.params.get("id"):

        db(db.input_invoice.id == request.params.get("id")).delete()

    redirect(URL('index'))

# Delete product in import invoice
@action('delete_import_product/<input_invoice_details_id:int>/<invoice_id:int>')
@action.uses(db, session, auth.user)
def delete(input_invoice_details_id, invoice_id=None):
    assert input_invoice_details_id, invoice_id is not None
    db(db.input_invoice_details.id == input_invoice_details_id).delete()

    redirect(URL('get-import-invoice', invoice_id))

# Create export invoice
@action('create_invoice', method=["POST"])
@action.uses(db, auth.user)
def create_export_invoice():
    if request.params.get("name"):

        db.output_invoice.insert(name=request.params.get("name"))
        invoice = db(db.output_invoice.name ==
                     request.params.get("name")).select()
        invoice_id = invoice[0].id

    redirect(URL('get_invoice', invoice_id))


# Create import invoice
@action('create_import_invoice', method=["POST"])
@action.uses(db, auth.user)
def create_import_invoice():
    if request.params.get("name"):

        db.input_invoice.insert(name=request.params.get("name"))
        invoice = db(db.input_invoice.name ==
                     request.params.get("name")).select()
        invoice_id = invoice[0].id

    redirect(URL('get-import-invoice', invoice_id))

# Delete export invoice
@action('delete_invoice', method=["POST"])
@action.uses(db, auth.user)
def delete_invoice():
    if request.params.get("id"):

        db(db.output_invoice.id == request.params.get("id")).delete()

    redirect(URL('index'))

# Delete product in export invoice
@action('delete_product/<output_invoice_details_id:int>/<invoice_id:int>')
@action.uses(db, session, auth.user)
def delete(output_invoice_details_id, invoice_id=None):
    assert output_invoice_details_id, invoice_id is not None
    db(db.output_invoice_details.id == output_invoice_details_id).delete()

    redirect(URL('get_invoice', invoice_id))

# Create a print hmtl for export invoice
@action('print-invoice/<invoice_id:int>', method=["GET"])
@action.uses(db, auth.user, 'hoadon.html')
def invoiceJson(invoice_id):
    total = 0
    total_product = []
    invoice = db(db.output_invoice.id == invoice_id).select()
    invoice_details = db(db.output_invoice.id == db.output_invoice_details.output_invoice_id ==  invoice_id).select()
    for i in invoice_details:
        total += int(i.total_price)
        total_product.append(i.product_id)

  
   
    # return dict json 
    products = db(db.product.id > 0).select()
    return dict(invoice=invoice, details = invoice_details, total = total, total_product = len(total_product), products = products)

# Update custome infor for export invoice
@action('customer-infor/<invoice_id:int>', method=["POST"])
@action.uses(db, auth.user)
def customer(invoice_id = None):
    assert invoice_id is not None
    invoice = db(db.output_invoice.id == invoice_id)
    invoice.update(customer_name=request.params.get("fullname"),customer_address=request.params.get("address"))
    

    redirect(URL('get_invoice', invoice_id))

# Get and calculate data for  report page
@action('statistic', method=["GET", "POST"])
@action.uses(db, auth.user, 'statistic.html')
def statistic():
    if request.method == "GET":
        return dict(output_invoice={}, dct={}, message={})
    else:
        fromDate = request.params.get("from")
        toDate = request.params.get("to")

        products = db(((db.output_invoice.id == db.output_invoice_details.output_invoice_id) & (db.output_invoice.created_at >= fromDate) & (db.output_invoice.created_at <= toDate))).select()
        import_products = db(((db.input_invoice.id == db.input_invoice_details.input_invoice_id) & (db.input_invoice.created_at >= fromDate) & (db.input_invoice.created_at <= toDate))).select()
    
        if len(products) == 0:
            return dict(output_invoice={}, message="Don't have enough data!")
        else:
            report = dict()
            import_report = dict()
   
 
            for p in products: # Tính số lượng hàng hóa xuất nếu chưa có thì thêm vô obj nếu đã có thì cộng thêm value vô đúng key
                if p.output_invoice_details.product_id in report:
                    report[p.output_invoice_details.product_id] += p.output_invoice_details.quantity
                else:
                    report[p.output_invoice_details.product_id] = p.output_invoice_details.quantity
            
            
            for i in import_products:
                if i.input_invoice_details.product_id in import_report:
                    import_report[i.input_invoice_details.product_id] += i.input_invoice_details.quantity
                else:
                    import_report[i.input_invoice_details.product_id] = i.input_invoice_details.quantity
         
            print(report)
         
            for i in report:
                print(i)
            arr = []
            productList = []
            for im in import_report:
                product = {
                    'name' : im,
                    'import' : import_report[im] , 
                    'export' : 0 
                }
                arr.append(im)
                productList.append(product)
            for ex in report:
                if ex not in arr:
                    product = {
                        'name' : ex, 
                        'import' : 0 ,
                        'export' : report[ex] #dict['key'] --> value
                    }
                    productList.append(product)
                else:
                    index = arr.index(ex)
                    productList[index]['export'] = report[ex] 

              
        
        return dict(output_invoice=products, report=report, import_report=import_report, fromDate=fromDate,toDate=toDate, productList=productList)



 
    

