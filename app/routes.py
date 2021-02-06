'''recipe Saver'''
import os
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from sqlalchemy.orm import sessionmaker
from app import app, db
from app.forms import LoginForm, AddRecipe, TagList, UpdateRecipe, AddTag
from app.models import Recipe, Tag, recipeTag
from app import Config
from werkzeug.utils import secure_filename
from flask import send_from_directory
from app.image import Image



@app.route('/',methods=['GET', 'POST'])
@app.route('/recipe_index', methods=['GET', 'POST'])
def recipe_index():
    """Return URL for recipe_index.html"""
    categories = [(c.id, c.name) for c in Tag.query.all()]
    AddForm = AddRecipe()
    AddForm.tags.choices = categories

    AddTagForm = AddTag()
    
    TagForm = TagList(request.form)  
    TagForm.tags.choices = categories
    
    recipes = Recipe.query.all()
    if request.method  == 'POST':
        if TagForm.validate_on_submit():
            if TagForm.search.data:
                print("TagForm submitted")
                tags_id = TagForm.tags.data
                recipes = []
                for tag_id in tags_id:
                    match = db.session.query(Recipe).filter(Recipe.tags.any(id=tag_id)).all()
                    recipes += match
            if TagForm.delete.data:
                tags_id = TagForm.tags.data
                for tag_id in tags_id:
                    Tag.query.filter_by(id=tag_id).delete()
                db.session.commit() 
                return redirect(url_for('recipe_index'))
        if AddForm.validate_on_submit():
            add_new_recipe(AddForm)
            return redirect(url_for('recipe_index'))
        if AddTagForm.validate_on_submit():
            add_tag(AddTagForm.name.data)
            return redirect(url_for('recipe_index'))
        else:
            print("Nothing")


    return render_template('recipe_index.html', title='Home Chef', form=TagForm, recipes=recipes, addform=AddForm, addTagForm=AddTagForm)

@app.route('/recipe/<recipe_id>',methods=['GET', 'POST'])
def recipe(recipe_id):
    recipe = Recipe.query.filter_by(id=recipe_id).first_or_404()
    recipe.ingredients = recipe.ingredients.split('\n')
    return render_template('recipe.html', title='Recipe', recipe=recipe, recipe_image=recipe.recipe_image)

@app.route('/<recipe_id>/update_recipe', methods=['GET', 'POST'])
def update_recipe(recipe_id):
    categories = [(c.id, c.name) for c in Tag.query.all()]
    recipe = Recipe.query.filter_by(id=recipe_id).first_or_404()
    form = UpdateRecipe(obj=recipe)
    AddTagForm = AddTag()

    form.tags.choices = categories
    if form.validate_on_submit():
        if form.submit.data:
            # If new image added, then update. Otherwise keep old image
            formDict = form.data
            if form.image_source_link.data:
                imageObj=Image(form.image_source_link.data)
                formDict.update(image_source_link=imageObj.imgur_url)
                formDict['recipe_image'] = formDict.pop('image_source_link') 
            for key, value in formDict.items():
                try:
                    setattr(recipe, key, value)
                except AttributeError:
                    pass
            tags = Tag.query.filter(Tag.id.in_(form.tags.data))
            recipe.tags.extend(tags)
            db.session.commit()
            return redirect(url_for('recipe', recipe_id=recipe_id))
    elif AddTagForm.validate_on_submit():
        add_tag(AddTagForm.name.data)
        AddTagForm.name.data=""
        categories = [(c.id, c.name) for c in Tag.query.all()]
        form.tags.choices = categories
    return render_template('edit_recipe.html', title='Update Recipe', form=form, recipes=recipe, addTagForm=AddTagForm)


#Delete recipe needs fixing
@app.route('/<recipe_id>/delete_recipe', methods=['GET', 'POST'])
def delete_recipe(recipe_id):
    #Delete the image from imgur
    imgur_delete_hash = Recipe.query.with_entities(Recipe.image_delete_hash).filter_by(id=recipe_id)
    Image.delete_image(imgur_delete_hash)

    #Then delete the recipe item from the database
    Recipe.query.filter_by(id=recipe_id).delete()
    db.session.commit()
    return redirect(url_for('recipe_index'))




def add_tag(tag_name):
    tag_name = tag_name.lower();
    if Tag.query.filter_by(name=tag_name).first():
        flash('Tag "{}" already exists'.format(
            tag_name))
    else:
        tag = Tag(
            name=tag_name,
        )
        db.session.add(tag)
        db.session.commit()
        flash('Successfully added tag: {}'.format(
            tag_name))


def add_new_recipe(AddForm):
    #returns the imgur hashed url
    imageObj=Image(AddForm.image_source_link.data)
    formDict = AddForm.data
    
    recipe = Recipe(
        title=AddForm.title.data.title(),
        author=AddForm.author.data,
        link=AddForm.link.data,
        ingredients=AddForm.ingredients.data,
        recipe_image=imageObj.imgur_url,
        rating = AddForm.rating.data,
        image_delete_hash = imageObj.imgur_delete_hash
    )     

    tags = Tag.query.filter(Tag.id.in_(AddForm.tags.data))
    recipe.tags.extend(tags)

    db.session.add(recipe)
    db.session.commit()

